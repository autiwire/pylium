"""
Type definitions for the manifest system.
All types are imported and re-exported here for convenient access.
"""

class ManifestTypes():
    from .xobject import XObject
    from .value import ManifestValue as Value
    Date = Value.Date
    
    from .version import ManifestVersion as Version
    from .location import ManifestLocation as Location
    from .objecttype import ManifestObjectType as ObjectType
    from .status import ManifestStatus as Status
    from .changelog import ManifestChangelog as Changelog
    from .dependency import ManifestDependency as Dependency

    from .author import ( 
        ManifestAuthor as Author, 
        ManifestAuthorList as AuthorList, 
        ManifestContributorList as ContributorList, 
        ManifestMaintainerList as MaintainerList 
    )

    from .license import (
        ManifestCopyright as Copyright, 
        ManifestLicense as License, 
        ManifestLicenseList as LicenseList,
        ManifestLicenses as Licenses
    )

    from .thread import ManifestThreadSafety as ThreadSafety
    from .accessmode import ManifestAccessMode as AccessMode
    from .ai import ManifestAIAccessLevel as AIAccessLevel
    
    from .frontend import ManifestFrontend as Frontend
    from .backend import (
        ManifestBackend as Backend, 
        ManifestBackendGroup as BackendGroup
    )

__all__ = [
    "ManifestTypes"
]