from ._component import _PackageComponent
from ._header import _PackageHeader

from abc import ABC, abstractmethod

class Package(ABC):
    """
    This is the package class for Pylium.
    A package is a collection of components that are used to build a project.
    A package can be a subpackage or a standalone package.
    This class contains nested classed which are the base classes for the components of the package.

    """

    Component = _PackageComponent
    Header = _PackageHeader

    def __init__(self):
        pass    

    @abstractmethod
    def _dont_create_objects_directly(self):
        """
        This method is used to prevent users from creating objects directly from the package class.
        """
        raise NotImplementedError("Package class cannot be instantiated directly.")
