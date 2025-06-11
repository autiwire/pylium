from .__header__ import Frontend, Header

class FrontendImpl(Frontend):
    """
    Default implementation of the Frontend class.
    
    This provides a basic concrete implementation of the abstract Frontend
    base class for testing and development purposes.
    """
    
    __class_type__ = Header.ClassType.Impl
    
    def __init__(self, **kwargs):
        """Initialize the frontend implementation."""
        super().__init__(**kwargs)
        self._running = False
    
    def start(self, **kwargs) -> None:
        """
        Start the frontend interface.
        
        Args:
            **kwargs: Additional startup parameters
        """
        if not self._running:
            self._running = True
            print(f"Frontend {self.__class__.__name__} started")
        else:
            print(f"Frontend {self.__class__.__name__} is already running")
    
    def stop(self, **kwargs) -> None:
        """
        Stop the frontend interface.
        
        Args:
            **kwargs: Additional shutdown parameters
        """
        if self._running:
            self._running = False
            print(f"Frontend {self.__class__.__name__} stopped")
        else:
            print(f"Frontend {self.__class__.__name__} is not running")
    
    def is_running(self) -> bool:
        """
        Check if the frontend is currently running.
        
        Returns:
            bool: True if the frontend is running, False otherwise
        """
        return self._running

    @property
    def manifest(self) -> Manifest:
        """Get the manifest associated with this frontend instance."""
        return self.__manifest__

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration dictionary for this frontend."""
        return {}

    def __str__(self) -> str:
        """String representation of the frontend."""
        return f"{self.__class__.__name__}(manifest={self.manifest.location.shortName})"

    def __repr__(self) -> str:
        """Detailed representation of the frontend."""
        return f"{self.__class__.__name__}(manifest={self.manifest.location.fqn}, running={self.is_running()})"
