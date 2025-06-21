"""
Changelog type for the manifest.
"""

# Pylium imports
from .value import ManifestValue
from .author import ManifestAuthor

# Standard library imports
from typing import Optional, List

class ManifestChangelog(ManifestValue):
    def __init__(self, version: Optional[str] = None, date: Optional[ManifestValue.Date] = None, author: Optional[ManifestAuthor] = None, notes: Optional[List[str]] = None):
        self.version = version
        self.date = date
        self.author = author
        self.notes = notes if notes is not None else []

    def __str__(self):
        return f"{self.version} ({self.date}) {self.author} {self.notes}"
    
    def __repr__(self):
        return f"{self.version} ({self.date}) {self.author} {self.notes}"