"""
Version type for the manifest.
"""

# Pylium imports
from .value import ManifestValue

# Standard imports
from typing import Any

# External imports
from packaging.version import Version as PackagingVersion
from pydantic import ConfigDict, Field, computed_field, field_validator

class ManifestVersion(ManifestValue):
    """A version type that uses packaging.Version internally."""
    
    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        json_encoders={PackagingVersion: lambda v: str(v)}
    )

    version: PackagingVersion = Field(..., description="Version object")

    def __init__(self, version: str | PackagingVersion, **kwargs):
        if isinstance(version, str):
            version = PackagingVersion(version)
        super().__init__(version=version, **kwargs)

    @field_validator("version", mode="before")
    @classmethod
    def _parse_version(cls, v):
        if isinstance(v, PackagingVersion):
            return v
        return PackagingVersion(str(v))

    @computed_field
    @property
    def string(self) -> str:
        """Get the string representation of the version."""
        return str(self.version)

    def __str__(self) -> str:
        return str(self.version)

    def __repr__(self) -> str:
        return f"ManifestVersion({self.version})"

    def __hash__(self) -> int:
        return hash(self.version)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ManifestVersion):
            return self.version == other.version
        if isinstance(other, str):
            return str(self.version) == other
        return False
    
