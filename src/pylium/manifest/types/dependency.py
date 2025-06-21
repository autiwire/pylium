"""
Types for the manifest.
"""

# Pylium imports
from .value import ManifestValue

# Standard library imports
from typing import Any
from enum import Enum


class ManifestDependencyType(Enum):
    PYLIUM = "pylium"
    PIP = "pip"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


class ManifestDependencyCategory(Enum):
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
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
    
    @property
    def description(self) -> str:
        return {
            ManifestDependencyCategory.BUILD: "Required for building the package",
            ManifestDependencyCategory.RUNTIME: "Required for running the package (minimal set)",
            ManifestDependencyCategory.AUTOMATIC: "Will be added automatically by the system if required",
            ManifestDependencyCategory.DEVELOPMENT: "Only needed for development/testing (optional)"
        }[self]


class ManifestDependencyDirection(Enum):
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
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
    
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


class ManifestDependency(ManifestValue):
    Type = ManifestDependencyType
    Category = ManifestDependencyCategory
    Direction = ManifestDependencyDirection
   
    def __init__(self, name: str, version: str, type: Type = Type.PIP, source: str = None, category: Category = Category.AUTOMATIC, direction: Direction = Direction.MINIMUM):
        self.type = type
        self.name = name
        self.version = version
        self.source = source
        self.category = category
        self.direction = direction

    def __str__(self):
        if self.source is not None:
            return f"{self.name} ({self.direction.sign} {self.version}) [{self.type.name}] @ {self.source} [{self.category}]"
        else:
            return f"{self.name} ({self.direction.sign} {self.version}) [{self.type.name}] [{self.category}]"
    
    def __repr__(self):
        if self.source is not None:
            return f"{self.name} ({self.direction.sign} {self.version}) [{self.type.name}] @ {self.source} [{self.category}]"
        else:
            return f"{self.name} ({self.direction.sign} {self.version}) [{self.type.name}] [{self.category}]"