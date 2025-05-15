"""
Pylium Components

The Component class is the base class for all Pylium components.

"""

from ._h import *

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
   
__all__ = ["Component", "ComponentPackage"] 


