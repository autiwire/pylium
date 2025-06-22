"""
Access mode type for the manifest.
"""

# Standard library imports
from enum import Enum
from typing import Any


class ManifestAccessMode(str, Enum):
    Sync = "sync"
    Async = "async"
    Hybrid = "hybrid"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestAccessMode):
            return False
        return self.value == other.value