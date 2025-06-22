"""
Types for the manifest.
"""

# Pylium imports
from .value import ManifestValue
from .version import ManifestVersion

# Standard library imports
from typing import Any, Optional
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


class ManifestDependencyTypes():
    """
    Types for dependencies.
    """
    Type = ManifestDependencyType
    Category = ManifestDependencyCategory
    Direction = ManifestDependencyDirection

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