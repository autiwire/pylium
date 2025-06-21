from pylium.core import __manifest__ as __parent_manifest_
from pylium.core.header import Manifest, Header, dlock, classProperty

from abc import abstractmethod
from typing import Optional, Any, Dict, List, ClassVar
import threading

__manifest__ : Manifest = __parent_manifest_.createChild(
    location=Manifest.Location(module=__name__, classname=None), 
    description="Frontend abstraction layer for multiple interface types (CLI, Web, API, etc.)",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,  
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 8), 
                           author=__parent_manifest_.authors.rraudzus,
                           notes=["Initial definition of pylium.core.frontend package manifest.",
                                  "Established foundation for multi-frontend support architecture"]),
    ]
)

_registered_frontends : List[type] = []
_registered_frontends_lock = threading.Lock()

class Frontend(Header):
    """
    Abstract base class for all frontend implementations.
    
    Provides a unified interface for different types of user interfaces
    including CLI, Web, API, and other interaction modes.
    """
    
    __manifest__ : Manifest = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="Abstract base class for all frontend implementations",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.NoFrontend,  
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 8),
                               author=__parent_manifest_.authors.rraudzus,
                               notes=["Initial implementation of Frontend base class",
                                      "Defined abstract interface for frontend implementations",
                                      "Established foundation for multi-frontend architecture"]),
            Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025, 6, 20),
                               author=__parent_manifest_.authors.rraudzus,
                               notes=["Cleaned up debug output for better readability",
                                      "Improved frontend registration logging",
                                      "Enhanced code clarity and maintainability"])
        ]
    )

    frontendType : ClassVar[Manifest.Frontend] = Manifest.Frontend.NoFrontend


    @classmethod
    def registerFrontend(cls):
        """
        Register a frontend class.
        """

        with _registered_frontends_lock:
#            print(f"Registering frontend: {cls.__name__}")
#            print(f"Current registered frontends: {[f.__name__ for f in _registered_frontends]}")
#            print(f"Frontend type: {cls.frontendType.name}")

            if cls not in _registered_frontends:
                _registered_frontends.append(cls)
#                print(f"Added {cls.__name__} to registered frontends")
#            else:
#                print(f"{cls.__name__} already registered")


    @classmethod
    def getFrontend(cls, frontend: Manifest.Frontend) -> type:        
        """Get the frontend class for a given frontend type."""

        with _registered_frontends_lock:
#            print(f"Getting frontend for {frontend.name}")
#            print(f"Registered frontends: {[f.__name__ for f in _registered_frontends]}")
            for frontend_class in _registered_frontends:
#                print(f"Checking frontend: {frontend_class.__name__} for {frontend.name}")
                frontend_type = frontend_class.frontendType
#                print(f"  Frontend type: {frontend_type.name}")
#                print(f"  Match: {frontend_type & frontend}")
                if frontend_type & frontend:
                    return frontend_class
            return None


    def __init__(self, manifest: Manifest, **kwargs):
        """
        Initialize the frontend with optional manifest and configuration.
        
        Args:
            manifest: Optional manifest for this frontend instance
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self._manifest : Manifest = manifest


    @property
    def manifest(self) -> Manifest:
        """Get the manifest associated with this frontend instance."""
        return self._manifest


    @abstractmethod
    def start(self, **kwargs) -> None:
        """
        Start the frontend interface.
        
        Args:
            **kwargs: Additional startup parameters
        """
        pass


    @abstractmethod
    def stop(self, **kwargs) -> None:
        """
        Stop the frontend interface.
        
        Args:
            **kwargs: Additional shutdown parameters
        """
        pass


    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the frontend is currently running.
        
        Returns:
            bool: True if the frontend is running, False otherwise
        """
        pass


    def __str__(self) -> str:
        """String representation of the frontend."""
        return f"{self.__class__.__name__}(manifest={self.manifest.location.fqnShort})"


    def __repr__(self) -> str:
        """Detailed representation of the frontend."""
        return f"{self.__class__.__name__}(manifest={self.manifest.location.fqn}, running={self.is_running()})"
