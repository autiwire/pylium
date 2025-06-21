"""
Object type for the manifest.
"""

# Standard library imports
from enum import Enum
from typing import Any, Set
from pydantic import computed_field


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
        """Check if this object type can contain another object type."""
        if ManifestObjectType._containment_matrix is None:
            raise RuntimeError("ManifestObjectType._containment_matrix is not initialized")
        if self not in ManifestObjectType._containment_matrix:
            raise RuntimeError(f"ManifestObjectType {self} is not in the containment matrix")
        if other not in ManifestObjectType._containment_matrix[self]:
            return False
        return True
    
    def canBeContainedIn(self, other: "ManifestObjectType") -> bool:
        """Check if this object type can be contained in another object type."""
        return other.canContain(self)
    
    @computed_field
    @property
    def possibleChildren(self) -> Set["ManifestObjectType"]:
        """Get the set of object types that can be children of this type."""
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