from ._h import *

try:
    from ._version import version as __version__
except ImportError:
    # This is a fallback for cases where the package is not installed
    # or _version.py has not been generated (e.g., a raw source checkout).
    __version__ = "0.0.0.unknown" # Or some other placeholder


class PyliumPackage(Package):
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Package.Date(2025, 5, 14))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Package.Date(2025, 5, 14)),
    ]

__all__ = ["Pylium", "PyliumPackage"]