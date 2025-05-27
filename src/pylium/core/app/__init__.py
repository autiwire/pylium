"""
Pylium Core App

This module contains the core functionality of the application.
It is used to create a CLI interface for the application as well as serving 
fastapi endpoints and celery tasks.
"""

from .__header__ import *

class AppPackage(Package):
    """
    This Package contains the core functionality of the application.
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Package.Date(2025, 5, 15))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Package.Date(2025, 5, 15)),
    ]

__all__ = ["App", "AppPackage"]