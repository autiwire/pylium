"""
Version type for the manifest.
"""

# Pylium imports
from .value import ManifestValue

# Standard imports
from typing import Any

# External imports
from packaging.version import Version as PackagingVersion
from pydantic import ConfigDict, Field, computed_field

class ManifestVersion(ManifestValue):
    """A version type that uses packaging.Version internally."""

    # Pydantic fields
    model_config = ConfigDict(arbitrary_types_allowed=True)

    version: PackagingVersion = Field(description="Version object")

    def __init__(self, version: str | PackagingVersion, **kwargs):
        if isinstance(version, str):
            version_obj = PackagingVersion(version)
        else:
            version_obj = version
        super().__init__(version=version_obj, **kwargs)

    @computed_field
    @property
    def string(self) -> str:
        """Get the string representation of the version."""
        return str(self.version)

    def __str__(self) -> str:
        return self.string

    def __repr__(self) -> str:
        return f"ManifestVersion({self.version})"
