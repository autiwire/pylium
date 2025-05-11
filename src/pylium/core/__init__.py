from .component import Component

from typing import Type, ClassVar, Optional, List
import datetime

# Import the heavy machinery
#
# Here you would import the heavy machinery, but do it in the impl module instead
# Here we only define the dependencies of the compontent for the install system to detect them automatically
#




class Core(Component):
    """
    Core component
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.debug(f"Initializing Core: {self.name}")

__all__ = ["Core"]