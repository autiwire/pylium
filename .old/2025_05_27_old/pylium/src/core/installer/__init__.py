from pylium.core.package import Package
from pylium.core.installer._h import Installer

from typing import ClassVar, List

class InstallerPackageInit(Package): 
    """
    A Python package, typically a directory containing an __init__.py file.
    Handles bootstrapping and installation of modules.
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Package.Date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Package.Date(2025, 5, 10)),
    ]

__all__ = ["Installer"]