"""
Version type for the manifest.
"""

# Standard imports
from typing import Any, Annotated
from enum import Enum
import re

# External imports
from packaging.version import Version as PackagingVersion
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class ManifestVersionDirection(str, Enum):
    """
    The direction of the version.
    """

    NONE = "none"
    MINIMUM = "minimum"
    EXACT = "exact"
    MAXIMUM = "maximum"
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestVersionDirection):
            return False
        return self.value == other.value
       
    @property
    def description(self) -> str:
        return _desc_map[self]
    
    @property
    def sign(self) -> str:
        return _sign_map[self]

    @classmethod
    def from_sign(cls, sign: str) -> "ManifestVersionDirection":
        return _sign_to_direction.get(sign, cls.NONE)


_sign_map = {
    ManifestVersionDirection.NONE: "",
    ManifestVersionDirection.MINIMUM: ">=",
    ManifestVersionDirection.EXACT: "==",
    ManifestVersionDirection.MAXIMUM: "<=",
}
_desc_map = {
    ManifestVersionDirection.NONE: "No direction",
    ManifestVersionDirection.MINIMUM: "Minimum version",
    ManifestVersionDirection.EXACT: "Exact version",
    ManifestVersionDirection.MAXIMUM: "Maximum version",
}
_sign_to_direction = {v: k for k, v in _sign_map.items()}


class ManifestVersionTypes():
    """Types for the version."""
    Direction = ManifestVersionDirection


class ManifestVersion(str, ManifestVersionTypes):
    """A version type that uses packaging.Version internally and behaves like a string."""

    def __new__(cls, version: str | PackagingVersion, direction: ManifestVersionDirection = ManifestVersionDirection.NONE):
        # Parse version and direction from string if needed
        if isinstance(version, str):
            m = re.match(r'^(>=|==|<=)?(.+)$', version.strip())
            if m:
                sign, ver = m.groups()
                if sign and direction == ManifestVersionDirection.NONE:
                    direction = ManifestVersionDirection.from_sign(sign)
                version = ver
            version = PackagingVersion(version)
        elif isinstance(version, PackagingVersion):
            ver = version
            version = str(version)
        else:
            raise ValueError(f"Invalid version type: {type(version)}")

        # Create the string representation
        sign = direction.sign if direction else ""
        obj = super().__new__(cls, f"{sign}{version}")
        
        # Store the parsed version and direction
        obj._version = ver
        obj._direction = direction
        return obj

    @property
    def version(self) -> PackagingVersion:
        """Get the underlying version object."""
        return self._version

    @property
    def direction(self) -> ManifestVersionDirection:
        """Get the version direction."""
        return self._direction

    @classmethod
    def from_string(cls, s: str) -> "ManifestVersion":
        """Create a version from a string."""
        m = re.match(r'^(>=|==|<=)?(.+)$', s.strip())
        if not m:
            raise ValueError(f"Invalid version string: {s}")
        sign, version = m.groups()
        direction = ManifestVersionDirection.from_sign(sign)
        return cls(version=version, direction=direction)

    def __repr__(self) -> str:
        return f"ManifestVersion('{str(self)}')"

    def __hash__(self) -> int:
        return hash((self._version, self._direction))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ManifestVersion):
            return self._version == other._version and self._direction == other._direction
        if isinstance(other, str):
            try:
                other_version = ManifestVersion.from_string(other)
                return self == other_version
            except ValueError:
                return False
        return False

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Define how Pydantic should handle this type."""
        def validate_from_str(value: str) -> "ManifestVersion":
            if isinstance(value, cls):
                return value
            return cls.from_string(str(value))

        from_str_schema = core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_plain_validator_function(validate_from_str),
        ])

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                from_str_schema,
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                return_schema=core_schema.str_schema(),
                when_used="json"
            ),
        )
    


    
