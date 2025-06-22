"""
Types for the manifest.
"""

# Pylium imports
from .value import ManifestValue
from .version import ManifestVersion

# Standard library imports
from typing import Any, Optional, Dict, List
from enum import Enum

# External imports
from pydantic import computed_field, Field


class ManifestDependencyType(str, Enum):
    PYLIUM = "pylium"
    PIP = "pip"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestDependencyType):
            return False
        return self.value == other.value


class ManifestDependencyCategory(str, Enum):
    """
    Priority/Criticality level for dependencies.
    Critical dependencies are required for basic functionality.
    """
    BUILD = "build"
    RUNTIME = "runtime"
    AUTOMATIC = "automatic"
    DEVELOPMENT = "development"
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestDependencyCategory):
            return False
        return self.value == other.value
        
    @computed_field
    @property
    def description(self) -> str:
        """Get the description of the dependency category."""
        return {
            ManifestDependencyCategory.BUILD: "Required for building the package",
            ManifestDependencyCategory.RUNTIME: "Required for running the package (minimal set)",
            ManifestDependencyCategory.AUTOMATIC: "Will be added automatically by the system if required",
            ManifestDependencyCategory.DEVELOPMENT: "Only needed for development/testing (optional)"
        }[self]


class ManifestDependencyDirection(str, Enum):
    """
    The direction of the dependency.
    """
        
    MINIMUM = "minimum"
    EXACT = "exact"
    MAXIMUM = "maximum"
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestDependencyDirection):
            return False
        return self.value == other.value
       
    @property
    def description(self) -> str:
        return {
            ManifestDependencyDirection.MINIMUM: "Minimum version of the dependency (default)",
            ManifestDependencyDirection.EXACT: "Exact version of the dependency",
            ManifestDependencyDirection.MAXIMUM: "Maximum version of the dependency"
        }[self]
    
    @property
    def sign(self) -> str:
        return {
            ManifestDependencyDirection.MINIMUM: ">=",
            ManifestDependencyDirection.EXACT: "==",
            ManifestDependencyDirection.MAXIMUM: "<="
        }[self]


class ManifestDependencyConflict(ManifestValue):
    """Information about a dependency conflict"""
    type: str  # Type of conflict (e.g. "exact_below_minimum", "multiple_exact", "no_valid_version")
    package: str  # Package name with conflict
    severity: str  # Severity level (e.g. "error", "warning")
    exact: Optional[Dict[str, str]] = None  # Details about exact version requirement
    minimum: Optional[Dict[str, str]] = None  # Details about minimum version requirement
    maximum: Optional[Dict[str, str]] = None  # Details about maximum version requirement
    versions: Optional[List[Dict[str, str]]] = None  # For multiple_exact conflicts


class ManifestDependencyStats(ManifestValue):
    """Statistics about dependencies"""
    total_dependencies: int
    total_modules: int
    conflicts: int
    by_category: Dict[str, int] = Field(default_factory=dict)  # Count by category
    by_type: Dict[str, int] = Field(default_factory=dict)  # Count by type


class ManifestDependencyTypes():
    """
    Types for dependencies.
    """
    Type = ManifestDependencyType
    Category = ManifestDependencyCategory
    Direction = ManifestDependencyDirection
    Conflict = ManifestDependencyConflict
    Stats = ManifestDependencyStats

ManifestDependencyTypes.Types = ManifestDependencyTypes


class ManifestDependency(ManifestValue, ManifestDependencyTypes):
    """A dependency in the manifest system."""
    
    type: ManifestDependencyTypes.Type = Field(
        default=ManifestDependencyTypes.Type.PIP,
        description="Type of the dependency"
    )
    name: str = Field(description="Name of the dependency")
    version: ManifestVersion = Field(description="Version of the dependency")
    source: Optional[str] = Field(
        default=None,
        description="Source URL or path for the dependency"
    )
    category: ManifestDependencyTypes.Category = Field(
        default=ManifestDependencyTypes.Category.AUTOMATIC,
        description="Category of the dependency"
    )
    direction: ManifestDependencyTypes.Direction = Field(
        default=ManifestDependencyTypes.Direction.MINIMUM,
        description="Version constraint direction"
    )

    def __str__(self) -> str:
        """Return a string representation of the dependency."""
        if self.source is not None:
            return f"{self.name} ({self.direction.sign} {self.version}) [{self.type.name}] @ {self.source} [{self.category}]"
        else:
            return f"{self.name} ({self.direction.sign} {self.version}) [{self.type.name}] [{self.category}]"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the dependency."""
        return str(self)
    
    def __hash__(self) -> int:
        return hash((self.name, self.version, self.type, self.category, self.direction, self.source))
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestDependency):
            return False
        return (self.name == other.name and
                self.version == other.version and
                self.type == other.type and
                self.category == other.category and
                self.direction == other.direction and
                self.source == other.source)
    

class ManifestDependencyList(ManifestValue):
    """Complete dependency analysis results"""
    dependencies: Dict[str, List[ManifestDependency]]


    @computed_field
    @property
    def conflicts(self) -> List[ManifestDependencyConflict]:
        """Get confilcts object"""

        dependencies = self.dependencies
    
        # Collect all versions of each package
        dep_versions = {}  # name -> [(version, direction, module)]
        for module, module_deps in dependencies.items():
            for dep in module_deps:
                if dep.type.name == "PIP":
                    dep_versions.setdefault(dep.name, []).append((dep.version, dep.direction, module))
        
        # Analyze conflicts
        conflicts = []
        for pkg_name, versions in dep_versions.items():
            if len(versions) > 1:
                exact_versions = [(v, m) for v, d, m in versions if d == ManifestDependency.Direction.EXACT]
                min_versions = [(v, m) for v, d, m in versions if d == ManifestDependency.Direction.MINIMUM]
                max_versions = [(v, m) for v, d, m in versions if d == ManifestDependency.Direction.MAXIMUM]
                
                # Case 1: Multiple different EXACT versions
                if len(exact_versions) > 1:
                    unique_versions = set(v for v, _ in exact_versions)
                    if len(unique_versions) > 1:
                        conflicts.append(ManifestDependency.Conflict(
                            type="multiple_exact",
                            package=pkg_name,
                            severity="error",
                            versions=[{"version": str(v), "module": m} for v, m in exact_versions]
                        ))
                
                # Case 2: Single EXACT version with incompatible constraints
                if len(exact_versions) == 1:
                    exact_ver, exact_module = exact_versions[0]
                    exact_version = exact_ver.version
                    
                    for min_ver, min_module in min_versions:
                        min_version = min_ver.version
                        if exact_version < min_version:
                            conflicts.append(ManifestDependency.Conflict(
                                type="exact_below_minimum",
                                package=pkg_name,
                                severity="error",
                                exact={"version": str(exact_ver), "module": exact_module},
                                minimum={"version": str(min_ver), "module": min_module}
                            ))
                    
                    for max_ver, max_module in max_versions:
                        max_version = max_ver.version
                        if exact_version > max_version:
                            conflicts.append(ManifestDependency.Conflict(
                                type="exact_above_maximum",
                                package=pkg_name,
                                severity="error",
                                exact={"version": str(exact_ver), "module": exact_module},
                                maximum={"version": str(max_ver), "module": max_module}
                            ))
                
                # Case 3: MIN/MAX constraints with no possible version
                if min_versions and max_versions:
                    highest_min = max([(v.version, v, m) for v, m in min_versions], key=lambda x: x[0])
                    lowest_max = min([(v.version, v, m) for v, m in max_versions], key=lambda x: x[0])
                    
                    if highest_min[0] > lowest_max[0]:
                        conflicts.append(ManifestDependency.Conflict(
                            type="no_valid_version",
                            package=pkg_name,
                            severity="error",
                            minimum={"version": str(highest_min[1]), "module": highest_min[2]},
                            maximum={"version": str(lowest_max[1]), "module": lowest_max[2]}
                        ))

        return conflicts
    

    @computed_field
    @property
    def stats(self) -> ManifestDependencyStats:
        """Get stats object"""

        # Collect statistics
        tmp_stats = ManifestDependency.Stats(
            total_dependencies=sum(len(deps) for deps in self.dependencies.values()),
            total_modules=len(self.dependencies),
            conflicts=len(self.conflicts),
            by_category={},  # Initialize empty dicts
            by_type={}
        )
    
        # Count by category and type
        for module_deps in self.dependencies.values():
            for dep in module_deps:
                # Category stats
                category = getattr(dep, 'category', None)
                if category:
                    category_name = category.name
                    tmp_stats.by_category[category_name] = tmp_stats.by_category.get(category_name, 0) + 1
                
                # Type stats
                type_name = dep.type.name
                tmp_stats.by_type[type_name] = tmp_stats.by_type.get(type_name, 0) + 1
    
        return tmp_stats

    @classmethod
    def fromManifest(cls, fqn_short: str, recursive: bool = True, type_filter: str = None, category_filter: str = None) -> "ManifestDependencyList":
        """
        Get the dependencies of the given object path
        """

        from pylium.manifest import Manifest
        manifest = Manifest.getManifest(fqn_short)
        if manifest is None:
            raise ValueError(f"No manifest found for path: {fqn_short}")
        
        return manifest.listDependencies(recursive, type_filter, category_filter)


ManifestDependencyTypes.List = ManifestDependencyList