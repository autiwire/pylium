from pylium.core.package import Package, Module

from typing import ClassVar, List
import datetime

class InstallerPackage(Package): 
    """
    A Python package, typically a directory containing an __init__.py file.
    """
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=datetime.date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=datetime.date(2025, 5, 10)),
        Module.ChangelogEntry(version="0.0.2", notes=["Added dependency"], date=datetime.date(2025, 5, 10)),
    ]
    dependencies: ClassVar[List[Module.Dependency]] = [
        Module.Dependency(name="setuptools", type=Module.Dependency.Type.PIP, version="65.5.0"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
