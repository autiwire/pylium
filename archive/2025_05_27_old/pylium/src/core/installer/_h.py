from pylium.core.module import Module
from pylium.core.component import Component

from typing import ClassVar, List
import datetime

class InstallerPackageHeader(Module):
    """
    A module for managing the installation of Pylium modules.
    """
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version=Manifest.Version("0.0.1"), since_date=datetime.date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version=Manifest.Version("0.0.1"), notes=["Initial release"], date=datetime.date(2025, 5, 10)),
        Module.ChangelogEntry(version=Manifest.Version("0.0.2"), notes=["Added dependency"], date=datetime.date(2025, 5, 10)),
    ]
    dependencies: ClassVar[List[Module.Dependency]] = [
        Module.Dependency(name="setuptools", type=Module.Dependency.Type.PIP, version=Manifest.Version("65.5.0")),
    ]

class Installer(Component):
    """
    A class for managing the installation of Pylium modules.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   

    def install(self):
        """
        Install the Pylium modules.
        """
        pass

