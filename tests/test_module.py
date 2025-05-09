from pylium.core.module import Module

from logging import getLogger

logger = getLogger(__name__)

TestModuleModule = Module()

logger.info(TestModuleModule)

# log all class variables
for attr in dir(TestModuleModule):
    if not attr.startswith('_'):
        value = getattr(TestModuleModule, attr)
        logger.info(f"{attr}: {value}")
