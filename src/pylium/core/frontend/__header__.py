from pylium.core import __manifest__ as __parent__
from pylium.manifest import Manifest
from pylium.core.header import Header

from abc import abstractmethod
from typing import Optional, Any, Dict

__manifest__ : Manifest = __parent__.createChild(
    location=Manifest.Location(module=__name__, classname=None), 
    description="Frontend abstraction layer for multiple interface types (CLI, Web, API, etc.)",
    status=Manifest.Status.Development,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 8), 
                           author=__parent__.authors.rraudzus,
                           notes=["Initial definition of pylium.core.frontend package manifest.",
                                  "Established foundation for multi-frontend support architecture"]),
    ]
)

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
        frontend=Manifest.Frontend.NoFrontend,  # Base class has no specific frontend
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 8),
                               author=__parent__.authors.rraudzus,
                               notes=["Initial implementation of Frontend base class",
                                      "Defined abstract interface for frontend implementations",
                                      "Established foundation for multi-frontend architecture"]),
        ]
    )

    def __init__(self, manifest: Optional[Manifest] = None, **kwargs):
        """
        Initialize the frontend with optional manifest and configuration.
        
        Args:
            manifest: Optional manifest for this frontend instance
            **kwargs: Additional configuration parameters
        """
        super().__init__(**kwargs)
        self._manifest = manifest or self.__manifest__
        self._config = kwargs

    @property
    def manifest(self) -> Manifest:
        """Get the manifest associated with this frontend instance."""
        return self._manifest

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration dictionary for this frontend."""
        return self._config

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
        return f"{self.__class__.__name__}(manifest={self.manifest.location.shortName})"

    def __repr__(self) -> str:
        """Detailed representation of the frontend."""
        return f"{self.__class__.__name__}(manifest={self.manifest.location.fqn}, running={self.is_running()})"
