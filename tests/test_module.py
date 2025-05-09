from pylium.core.module import Module
from pylium.core.package import Package
from pylium.core.project import Project

from logging import getLogger

logger = getLogger(__name__)

TestModuleModule = Module()

logger.info(TestModuleModule)

# log all class variables
for attr in dir(TestModuleModule):
    if not attr.startswith('_'):
        value = getattr(TestModuleModule, attr)
        logger.info(f"{attr}: {value}")

TestPackage = Package()

logger.info(TestPackage)

# log all class variables
for attr in dir(TestPackage):
    if not attr.startswith('_'):
        value = getattr(TestPackage, attr)
        logger.info(f"{attr}: {value}")

TestProject = Project()

logger.info(TestProject)

# log all class variables
for attr in dir(TestProject):
    if not attr.startswith('_'):
        value = getattr(TestProject, attr)
        logger.info(f"{attr}: {value}")

