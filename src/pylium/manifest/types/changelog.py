"""
Changelog type for the manifest.
"""

# Pylium imports
from .value import ManifestValue
from .author import ManifestAuthor
from .version import ManifestVersion

# Standard library imports
from typing import List, Optional, Any

# External imports
from pydantic import Field

class ManifestChangelog(ManifestValue):
    """
    Changelog entry for a manifest.
    Contains version, date, author, and notes.
    """
    version: ManifestVersion = Field(description="Version number for this changelog entry")
    date: ManifestValue.Date = Field(description="Date of this changelog entry")
    author: Optional[ManifestAuthor] = Field(default=None, description="Author of this changelog entry")
    notes: List[str] = Field(default_factory=list, description="List of changes in this entry")

    def __str__(self) -> str:
        """Return a string representation of the changelog entry."""
        return f"{self.version} ({self.date}): {', '.join(self.notes)}"

    def __repr__(self) -> str:
        """Return a detailed string representation of the changelog entry."""
        return f"Changelog(version={self.version}, date={self.date}, author={self.author}, notes={self.notes})"
    
    def __hash__(self) -> int:
        return hash((self.version, self.date, self.author, tuple(self.notes)))
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestChangelog):
            return False
        return (self.version == other.version and
                self.date == other.date and
                self.author == other.author and
                self.notes == other.notes)
       