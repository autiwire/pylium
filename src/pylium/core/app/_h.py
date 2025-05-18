from pylium.core.package import Package
from pylium.core.module import Module
from pylium.core.component import Component

from typing import ClassVar, List, Optional, Type
import enum

class AppPackageHeader(Package):
    """
    This Package contains the core functionality of the application.
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Package.Date(2025, 5, 15))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Package.Date(2025, 5, 15)),
    ]
    dependencies: ClassVar[List[Package.Dependency]] = [
        Package.Dependency(name="pydantic", type=Package.Dependency.Type.PIP, version="2.10.2"),
        Package.Dependency(name="fire", type=Package.Dependency.Type.PIP, version="0.5.0"),
        Package.Dependency(name="fastapi", type=Package.Dependency.Type.PIP, version="0.105.1"),
        Package.Dependency(name="uvicorn", type=Package.Dependency.Type.PIP, version="0.25.0"),
    ]

class AppRunMode(enum.Enum):
    CLI = "cli"
    API = "api"
    TASK = "task"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value

class App(Component):
    """
    This class is the main entry point for the application.
    """

    RunMode = AppRunMode

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, run_mode: RunMode, cli_entry: Optional[Type[Module]|Type[Component]] = None):
        raise NotImplementedError("Implement this method in implementation class")


