"""
Status type for the manifest.
"""

# Standard library imports
from enum import Enum


class ManifestStatus(Enum):
    Development = "Development"
    Production = "Production"
    Deprecated = "Deprecated"
    Unstable = "Unstable"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value