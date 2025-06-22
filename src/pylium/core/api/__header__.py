from pylium.core import __manifest__ as __parent_manifest__
from pylium.core.header import Manifest, Header
from pylium.core.frontend import Frontend

from typing import ClassVar

__manifest__: Manifest = __parent_manifest__.createChild(
    location=Manifest.Location(module=__name__, classname=None),
    description="API module",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.API,
    dependencies=[  Manifest.Dependency(name="fastapi", version=Manifest.Version(">=0.115.6"), type=Manifest.Dependency.Type.PIP, category=Manifest.Dependency.Category.RUNTIME),
                    Manifest.Dependency(name="fastapi", version=Manifest.Version("==0.110.0"), type=Manifest.Dependency.Type.PIP, category=Manifest.Dependency.Category.RUNTIME, direction=Manifest.Dependency.Direction.EXACT) ],
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,6,15), author=__parent_manifest__.authors.rraudzus, 
                                 notes=["Initial release"]),
        Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025,6,15), author=__parent_manifest__.authors.rraudzus, 
                                 notes=["Added __manifest__ for module"]),
        Manifest.Changelog(version=Manifest.Version("0.1.2"), date=Manifest.Date(2025,6,15), author=__parent_manifest__.authors.rraudzus, 
                                 notes=["Changed base class to Frontend, added frontend registration"]),
    ]
)

class API(Frontend):
    """
    The API header class that defines the interface for the API implementation.
    This class is responsible for defining the API interface that will be implemented
    by the concrete implementation class.
    """

    __manifest__ : Manifest = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="The core API building component for Pylium.",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.API,
        changelog=[
            Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,6,15), author=__parent_manifest__.authors.rraudzus, 
                                 notes=["Initial release"]),
            Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025,6,15), author=__parent_manifest__.authors.rraudzus, 
                                 notes=["Added __manifest__ for API class"]),
            Manifest.Changelog(version=Manifest.Version("0.1.2"), date=Manifest.Date(2025,6,15), author=__parent_manifest__.authors.rraudzus, 
                                 notes=["Updated to use Frontend base class, added frontendType"]),
        ]
    )

    frontendType : ClassVar[Manifest.Frontend] = Manifest.Frontend.API

    def __init__(self, manifest: Manifest, **kwargs):
        """
        Initialize the API header with a manifest.

        Args:
            manifest: The manifest that describes the API structure.
        """
        super().__init__(manifest)
        self._target_manifest = manifest

# Register the API frontend to the Frontend registry
# This is done here to avoid circular imports
# Registration makes the frontend available to the Frontend.getFrontend() method
# so that the AppImpl can find the Frontend and instantiate it.
API.registerFrontend()