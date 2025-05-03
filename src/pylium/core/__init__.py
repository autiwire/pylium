from .component import Component

from typing import Type, ClassVar, Optional, List
import datetime

# Import the heavy machinery
#
# Here you would import the heavy machinery, but do it in the impl module instead
# Here we only define the dependencies of the compontent for the install system to detect them automatically
#


class CoreConfig(Component.Module.Config):
    """
    Configuration for the core component
    """
    pass

pylium = Component.Module(
    name=__name__,
    version="0.2.0",
    description="Pylium core component",
    dependencies=[],
    authors=[
        Component.Module.AuthorInfo(name="John Doe", email="john.doe@example.com", since_version="0.2.0", since_date=datetime.date(2022, 2, 2))
    ],
    settings_class=CoreConfig,
)
logger = pylium.logger

class Core(Component):
    """
    Core component
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.debug(f"Initializing Core: {self.name}")

__all__ = ["Core"]