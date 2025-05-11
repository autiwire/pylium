from pylium.core.module import Module
from pylium.core.package import Package
from pylium.core.project import Project

from typing import ClassVar, List
import datetime

from logging import getLogger

logger = getLogger(__name__)

def _log_class(cls):
    logger.info(f"Class: {cls.__name__}")
    logger.info(cls)

    for attr in dir(cls):
        if not attr.startswith('_'):
            value = getattr(cls, attr)
            logger.debug(f"{attr}: {value}")

#    logger.info("--------------------------------")
#    logger.info(f"Object: {cls()}")
#    logger.info("--------------------------------")

    logger.info("--------------------------------")


_log_class(Module)
_log_class(Package)
_log_class(Project)

class CustomModule(Module):
    """
    A custom module for testing.
    """
#    name: ClassVar[str] = "CUSTOM_A"
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="John Doe", email="john.doe@example.com", since_version="0.0.1", since_date=datetime.date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=datetime.date(2025, 5, 10)),
        Module.ChangelogEntry(version="0.0.2", notes=["Added dependency"], date=datetime.date(2025, 5, 10)),
        Module.ChangelogEntry(version="0.0.3", notes=["Added CustomModule test"], date=datetime.date(2025, 5, 10)),
    ]
    # Add parents dependencies
    dependencies: ClassVar[List[Module.Dependency]] =  [
        Module.Dependency(name="test-custom-dep", type=Module.Dependency.Type.PIP, version="1.33.7"),
    ]
    
_log_class(CustomModule)


logger.info("Listing all modules:")

module_list = Module.list()
module_list.append(CustomModule)

for cls in module_list:
    logger.info(f"Module: {cls.__name__}")
    logger.debug(f"  Module: {cls}")
    logger.debug(f"    Dependencies: {cls.get_system_dependencies()}")
