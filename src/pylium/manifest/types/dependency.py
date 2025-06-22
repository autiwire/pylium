"""
Types for the manifest.
"""

# Pylium imports
from .xobject import XObject
from .value import ManifestValue
from .version import ManifestVersion, ManifestVersionDirection

# Standard library imports
from typing import Any, Optional, Dict, List
from enum import Enum

# External imports
from pydantic import computed_field, Field, ConfigDict


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
    Version = ManifestVersion
    Direction = Version.Direction
    Conflict = ManifestDependencyConflict
    Stats = ManifestDependencyStats

ManifestDependencyTypes.Types = ManifestDependencyTypes


class ManifestDependency(ManifestValue, ManifestDependencyTypes):
    """A dependency in the manifest system."""
    
    __style__: XObject.Style = XObject.Style.LINEAR

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

    def __str__(self) -> str:
        """Return a string representation of the dependency."""
        parts = [
            f"type={self.type}",
            f"name={self.name}",
            f"version={self.version}",
            f"source={self.source or 'None'}",
            f"category={self.category}"
        ]
        return ", ".join(parts)
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the dependency."""
        return str(self)
    
    def __hash__(self) -> int:
        return hash((self.name, self.version, self.type, self.category, self.source))
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestDependency):
            return False
        return (self.name == other.name and
                self.version == other.version and
                self.type == other.type and
                self.category == other.category and
                self.source == other.source)


class ManifestDependencyList(ManifestValue):
    """A list of dependencies grouped by module."""
    dependencies: Dict[str, List[ManifestDependency]] = Field(default_factory=dict)

    __style__: XObject.Style = XObject.Style.TREE

    @computed_field
    @property
    def conflicts(self) -> List[ManifestDependency.Conflict]:
        """Get a list of conflicts for this dependency."""
        conflicts = []
        dep_versions = {}

        # Group versions by package name
        for module, deps in self.dependencies.items():
            for dep in deps:
                dep_versions.setdefault(dep.name, []).append((dep.version, dep.version.direction, module))

        # Check for conflicts
        for pkg_name, versions in dep_versions.items():
            if len(versions) > 1:
                exact_versions = [(v, m) for v, d, m in versions if d == ManifestDependency.Direction.EXACT]
                min_versions = [(v, m) for v, d, m in versions if d == ManifestDependency.Direction.MINIMUM]
                max_versions = [(v, m) for v, d, m in versions if d == ManifestDependency.Direction.MAXIMUM]
                
                #print(exact_versions, min_versions, max_versions)

                # Case 1: Multiple different EXACT versions
                if len(exact_versions) > 1:
                    unique_versions = set(str(v) for v, _ in exact_versions)
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
                    
                    # Check minimum version constraints
                    for min_ver, min_module in min_versions:
                        if str(exact_ver) < str(min_ver):  # Use string comparison for proper version comparison
                            conflicts.append(ManifestDependency.Conflict(
                                type="exact_below_minimum",
                                package=pkg_name,
                                severity="error",
                                exact={"version": str(exact_ver), "module": exact_module},
                                minimum={"version": str(min_ver), "module": min_module}
                            ))
                    
                    # Check maximum version constraints
                    for max_ver, max_module in max_versions:
                        if str(exact_ver) > str(max_ver):  # Use string comparison for proper version comparison
                            conflicts.append(ManifestDependency.Conflict(
                                type="exact_above_maximum",
                                package=pkg_name,
                                severity="error",
                                exact={"version": str(exact_ver), "module": exact_module},
                                maximum={"version": str(max_ver), "module": max_module}
                            ))
                
                # Case 3: MIN/MAX constraints with no possible version
                if min_versions and max_versions:
                    # Find highest minimum version and lowest maximum version
                    highest_min = max(min_versions, key=lambda x: str(x[0]))
                    lowest_max = min(max_versions, key=lambda x: str(x[0]))
                    
                    # Check if there's a gap between min and max
                    if str(highest_min[0]) > str(lowest_max[0]):
                        conflicts.append(ManifestDependency.Conflict(
                            type="no_valid_version",
                            package=pkg_name,
                            severity="error",
                            minimum={"version": str(highest_min[0]), "module": highest_min[1]},
                            maximum={"version": str(lowest_max[0]), "module": lowest_max[1]}
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
    def fromManifest(cls, manifest: str | object, recursive: bool = True, type_filter: str = None, category_filter: str = None) -> "ManifestDependencyList":
        """
        Get the dependencies of the given manifest path or manifest object
        """

        from pylium.manifest import Manifest

        if isinstance(manifest, str):
            try:
                manifest = Manifest.getManifest(manifest)
            except ValueError:
                raise ValueError(f"No manifest found for path: {manifest}")
        elif isinstance(manifest, Manifest):
            pass
        else:
            raise ValueError(f"Invalid manifest type: {type(manifest)}")

        return manifest.listDependencies(recursive=recursive, type_filter=type_filter, category_filter=category_filter)



ManifestDependencyTypes.List = ManifestDependencyList