# Component Implementation - Demo implementation

from ._component import Component

# Import the heavy machinery
# 
# Here you would import the heavy machinery, especially in regards of dependencies
# This is the only place where you should import external libraries
#
# Example:
# from my_heavy_machinery import MyHeavyMachinery
#
# By importing here instead of the Header class, we can check dependencies before they are needed
# and fail early or install missing dependencies automatically.

import logging
logger = logging.getLogger(__name__)

# Create a Impl class that inherits from the Component class
class ComponentImpl(Component):
    """
    Implementation class for Component
    """

    # Set the _is_impl attribute to True -> this tells the Component class that this is an implementation
    _is_impl = True

    # Implement the __init__ method to initialize the compontent
    # Here you setup the heavy machinery, like loading data, initializing objects, etc.
    def __init__(self, *args, **kwargs):
        logger.debug(f"ComponentImpl __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

