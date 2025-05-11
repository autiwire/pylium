"""
Pylium Core Components

This module contains the base classes for core components of Pylium.

The Component class is the base class for all Pylium components.

"""

from pylium.core.package import Package
from ._h import Component

from typing import ClassVar, List

class ComponentPackage(Package):
    """
    Package for Pylium core components
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Package.Date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Package.Date(2025, 5, 10)),
    ]
   
__all__ = ["Component"]