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

    logger.info("--------------------------------")
    logger.info(f"Object: {cls()}")
    logger.info("--------------------------------")

    logger.info("\n\n")


_log_class(Module)
_log_class(Package)
_log_class(Project)



class CustomModule(Module):
    """
    A custom module for testing.
    """
    name: ClassVar[str] = "CUSTOMA"
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1x", notes=["Initial release"], date=datetime.date(2025, 5, 10))
    ]

_log_class(CustomModule)

class CustomPackage(Package):
    """
    A custom package for testing.
    """
    name: ClassVar[str] = "CUSTOMB"
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1y", notes=["Initial release"], date=datetime.date(2025, 5, 10))
    ]

_log_class(CustomPackage)

class CustomProject(Project):
    """
    A custom project for testing.
    """
    name: ClassVar[str] = "CUSTOMC"
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1z", notes=["Initial release"], date=datetime.date(2025, 5, 10))
    ]

_log_class(CustomProject)


# log all class variables
#for attr in dir(CustomModule):
#    if not attr.startswith('_'):
#        value = getattr(CustomModule, attr)
#        logger.info(f"{attr}: {value}")


