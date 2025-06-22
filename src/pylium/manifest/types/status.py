"""
Status type for the manifest.
"""

# Standard library imports
from enum import Enum
from typing import Any


class ManifestStatus(str, Enum):
    Development = "Development"
    Production = "Production"
    Deprecated = "Deprecated"
    Unstable = "Unstable"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestStatus):
            return False
        return self.value == other.value