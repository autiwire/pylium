"""
Access mode type for the manifest.
"""

# Standard library imports
from enum import Enum


class ManifestAccessMode(Enum):
    Sync = "sync"
    Async = "async"
    Hybrid = "hybrid"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
