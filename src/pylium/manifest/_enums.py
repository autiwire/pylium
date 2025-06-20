from enum import Enum
from typing import Any, ClassVar, Dict, Set

class ManifestObjectType(Enum):
    """
    The type of object that the manifest is describing.
    """
    Invalid = "invalid"
    Package = "package"
    Module = "module"
    Class = "class"
    Method = "method"
    Function = "function"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestObjectType):
            return False
        return self.value == other.value
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
    
    def canContain(self, other: "ManifestObjectType") -> bool:
        if ManifestObjectType._containment_matrix is None:
            raise RuntimeError("ManifestObjectType._containment_matrix is not initialized")
        if self not in ManifestObjectType._containment_matrix:
            raise RuntimeError(f"ManifestObjectType {self} is not in the containment matrix")
        if other not in ManifestObjectType._containment_matrix[self]:
            return False
        return True
    
    def canBeContainedIn(self, other: "ManifestObjectType") -> bool:
        return other.canContain(self)
    
    def possibleChildren(self) -> Set["ManifestObjectType"]:
        if ManifestObjectType._containment_matrix is None:
            raise RuntimeError("ManifestObjectType._containment_matrix is not initialized")
        if self not in ManifestObjectType._containment_matrix:
            return Set[ManifestObjectType]()
        return ManifestObjectType._containment_matrix[self]


ManifestObjectType._containment_matrix = {
    ManifestObjectType.Package: {ManifestObjectType.Package, ManifestObjectType.Module, ManifestObjectType.Class, ManifestObjectType.Function},
    ManifestObjectType.Module: {ManifestObjectType.Class, ManifestObjectType.Function},
    ManifestObjectType.Class: {ManifestObjectType.Method},
    ManifestObjectType.Method: {},
    ManifestObjectType.Function: {}
}


class ManifestDependencyType(Enum):
    PYLIUM = "pylium"
    PIP = "pip"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


class ManifestDependencyPriority(Enum):
    """
    Priority/Criticality level for dependencies.
    Critical dependencies are required for basic functionality.
    """
    AUTOMATIC = "automatic"    # Will be added automatically by the system if required
    SYSTEM = "system"      # Required for basic functionality (e.g., fire for CLI, packaging for versioning)
    DEVELOPMENT = "development" # Only needed for development/testing
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestDependencyPriority):
            return False
        return self.value == other.value
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
    
    @property
    def description(self) -> str:
        return {
            ManifestDependencyPriority.AUTOMATIC: "Will be added automatically by the system if required",
            ManifestDependencyPriority.SYSTEM: "Required for basic functionality (e.g., fire for CLI, packaging for versioning)",
            ManifestDependencyPriority.DEVELOPMENT: "Only needed for development/testing"
        }[self]


class ManifestStatus(Enum):
    Development = "Development"
    Production = "Production"
    Deprecated = "Deprecated"
    Unstable = "Unstable"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


class ManifestAccessMode(Enum):
    Sync = "sync"
    Async = "async"
    Hybrid = "hybrid"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


class ManifestThreadSafety(Enum):
    Unsafe     = "unsafe"
    Reentrant  = "reentrant"
    ThreadSafe = "thread-safe"
    ActorSafe  = "actor-safe"
    Immutable  = "immutable"

    def __str__(self):
        return f"{self.name.lower()}"

    def __repr__(self):
        return f"{self.name.lower()}"

    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestThreadSafety):
            return False
        return self.value == other.value
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    @property
    def description(self) -> str:
        return {
            ManifestThreadSafety.Unsafe: "No synchronization, may cause race conditions.",
            ManifestThreadSafety.Reentrant: "Reentrant for single thread recursion, not parallel-safe.",
            ManifestThreadSafety.ThreadSafe: "Internally synchronized for parallel access.",
            ManifestThreadSafety.ActorSafe: "Thread-safe via actor/queue-based serialized access.",
            ManifestThreadSafety.Immutable: "Immutable after creation, safe by design."
        }[self]