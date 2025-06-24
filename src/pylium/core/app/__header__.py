from pylium.core import __manifest__ as __parent_manifest__
from pylium.manifest import Manifest
from pylium.core.header import Header, classProperty, dlock

import threading
from abc import abstractmethod
from typing import Type, Optional

__manifest__ : Manifest = Manifest(
    parent=__parent_manifest__,
    location=Manifest.Location(module=__name__, classname=None), 
    description="Application management and execution module",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025, 5, 28), 
                           author=__parent_manifest__.authors.rraudzus,
                           notes=["Initial definition of pylium.core.app package manifest."]),
        Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025, 6, 8),
                           author=__parent_manifest__.authors.rraudzus,
                           notes=["Implemented recursive CLI system with tree-based command structure",
                                  "Added support for both flat (module_h.py) and nested (module/__header__.py) patterns",
                                  "Fixed CLI visibility to show locally defined classes and Header base class"]),
        Manifest.Changelog(version=Manifest.Version("0.1.2"), date=Manifest.Date(2025,6,11), author=__parent_manifest__.authors.rraudzus,
                                 notes=["Added __parent_manifest__ to the app module manifest to allow for proper manifest resolution"]),
    ]
)

class App(Header):
    """
    Application management and execution class

    This class uses a lazy-loaded, singleton pattern for its default instance,
    which is accessible via the `App.default` class property.

    To use a custom subclass as the default, register it *before* first
    accessing `App.default`:
    `App.set_default_class(YourCustomApp)`

    If you need a separate, isolated application environment, you can
    instantiate it directly: `my_new_app = App()`
    """

    Frontend = Manifest.Frontend

    __manifest__ : Manifest = Manifest(
        parent=__manifest__,
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="Application management and execution class",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.CLI,
        changelog=[
            Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025, 5, 28),
                               author=__parent_manifest__.authors.rraudzus,
                               notes=["Initial definition of pylium.core.app package manifest."]),
            Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025, 5, 28),
                               author=__parent_manifest__.authors.rraudzus,
                               notes=["Enhanced CLI integration with recursive navigation support",
                                      "App class now properly discoverable in CLI tree structure",
                                      "Consistent behavior between direct and recursive CLI access"]),
        ]
    )

    _default_instance: "App" = None
    _default_class: type = None
    _default_lock = threading.Lock()

    @abstractmethod
    @Manifest.func(Manifest(
        parent=__manifest__,
        location=None,
        description="Test function for the App class",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.CLI,
        changelog=[
            Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,6,13), author=__parent_manifest__.authors.rraudzus,
                                 notes=["Initial release"]),
        ]
    ))
    def test(self):
        """
        Test function for the App class
        """
        print("test")


    @classmethod
    @Manifest.func(Manifest(
        parent=__manifest__,
        location=None,
        description="Test2 function for the App class",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.CLI,
        changelog=[
            Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,6,13), author=__parent_manifest__.authors.rraudzus,
                                 notes=["Initial release"]),
        ]
    ))
    def test2(cls):
        """
        Test2 function for the App class
        """
        from .__impl__ import AppImpl 
        return AppImpl._find_impl(specific_header_cls=cls)


    @classmethod
    def set_default_class(cls, app_class: type):
        """
        Registers a subclass to be used for the default instance.

        This must be called before the default instance is first accessed.

        :param app_class: The class to use (must be a subclass of App).
        """
        if not issubclass(app_class, cls):
            raise TypeError(f"{app_class.__name__} must be a subclass of {cls.__name__}")
        if cls._default_instance is not None:
            raise RuntimeError("Cannot change default app class after instance has been created.")
        cls._default_class = app_class

    @classProperty
    @dlock("_default_lock", "_default_instance")
    def default(cls) -> "App":
        """
        The default, shared instance of the App.

        This is a lazy-loaded property that returns the singleton instance
        of the configured App class (e.g., `App` or a registered subclass).
        """
        # If a custom class was not set, use App itself as the default.
        if cls._default_class is None:
            cls._default_class = cls
        return cls._default_class()


    @property
    def frontend(self) -> Optional[Frontend]:
        """Get the frontend associated with this app instance."""
        with self._frontend_lock:
            return self._frontend


    @frontend.setter
    def frontend(self, frontend: Frontend):
        """Set the frontend associated with this app instance."""
        with self._frontend_lock:
            self._frontend = frontend


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._frontend : Optional[Manifest.Frontend] = None
        self._frontend_lock: threading.Lock = threading.Lock()


    @abstractmethod
    def run(self, frontend: Type[Frontend], manifest: Manifest):
        """
        Runs the application component based on its manifest.

        This is an abstract method that must be implemented by a subclass,
        typically in the corresponding `__impl__.py` file.
        """
        pass

