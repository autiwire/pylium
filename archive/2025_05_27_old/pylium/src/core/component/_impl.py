# Component Implementation - Demo implementation

from ._h import *

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

class ComponentPackageImpl(Package):
    """
    This Package contains the core functionality of the component.
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version=Manifest.Version("0.0.1"), since_date=Package.Date(2025, 5, 15))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version=Manifest.Version("0.0.1"), notes=["Initial release"], date=Package.Date(2025, 5, 15)),
    ]

logger = ComponentPackageImpl.logger

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

