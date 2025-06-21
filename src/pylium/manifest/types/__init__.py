"""
Type definitions for the manifest system.
All types are imported and re-exported here for convenient access.
"""

from .xobject import XObject
from .value import ManifestValue
from .accessmode import ManifestAccessMode
from .ai import ManifestAIAccessLevel
from .author import ( 
    ManifestAuthor, 
    ManifestAuthorList, 
    ManifestContributorList, 
    ManifestMaintainerList 
)
from .backend import (
    ManifestBackend, 
    ManifestBackendGroup
)
from .changelog import ManifestChangelog
from .dependency import (
    ManifestDependency,
    ManifestDependencyCategory,
    ManifestDependencyDirection,
    ManifestDependencyType,
)
from .frontend import ManifestFrontend
from .license import (
    ManifestCopyright, 
    ManifestLicense, 
    ManifestLicenseList,
    ManifestLicenses
)
from .location import ManifestLocation
from .objecttype import ManifestObjectType
from .status import ManifestStatus
from .thread import ManifestThreadSafety

__all__ = [
    # Base classes
    "XObject",
    "ManifestValue",

    # Core types
    "ManifestAccessMode",
    "ManifestAIAccessLevel",
    "ManifestAuthor",
    "ManifestAuthorList",
    "ManifestBackend",
    "ManifestBackendGroup",
    "ManifestChangelog",
    "ManifestContributorList",
    "ManifestCopyright",
    "ManifestDependency",
    "ManifestDependencyCategory",
    "ManifestDependencyDirection",
    "ManifestDependencyType",
    "ManifestFrontend",
    "ManifestLicense",
    "ManifestLicenseList",
    "ManifestLicenses",
    "ManifestLocation",
    "ManifestMaintainerList",
    "ManifestObjectType",
    "ManifestStatus",
    "ManifestThreadSafety",
]