from pylium import __project__
from pylium.core.header import Header
from pylium.manifest import Manifest


__manifest__: Manifest = __project__.__manifest__.createChild(
    location=Manifest.Location(module=__name__, classname=None),
    description="CLI module",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    dependencies=[],
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,6,6), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Initial release"]),
        Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,6,6), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Added __manifest__ for module"]),
        Manifest.Changelog(version="0.2.0", date=Manifest.Date(2025,6,8), author=__project__.__manifest__.authors.rraudzus,
                                 notes=["Complete architectural overhaul to tree-based CLI system",
                                        "Implemented CommandNode and CommandTree classes for canonical command structure",
                                        "Added CLIRenderer for python-fire frontend compatibility",
                                        "Support for both flat (module_h.py) and nested (module/__header__.py) file patterns",
                                        "Fixed manifest resolution to prefer header manifests over module manifests",
                                        "Implemented proper visibility checking for locally defined vs imported classes",
                                        "Added categorization support (CLASS, COMMANDS, SUBMODULES) with fire categories",
                                        "Ensured recursive CLI calls behave identically to direct module calls"]),
    ]
)

class CLI(Header):
    """
    A component that recursively builds and runs a command-line interface.
    """

    __manifest__ = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="The core CLI building component for Pylium.",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.CLI,
        changelog=[
            Manifest.Changelog(version="0.2.0", date=Manifest.Date(2025,6,8), author=__project__.__manifest__.authors.rraudzus,
                               notes=["Redesigned CLI class with tree-based architecture",
                                      "Replaced dynamic class building with CommandTree/CommandNode approach", 
                                      "Added support for recursive navigation with consistent behavior",
                                      "Enhanced manifest discovery for proper header resolution",
                                      "CLI now serves as frontend-agnostic command tree builder"]),
        ]
    )

    def __init__(self, manifest: Manifest):
        """
        Initializes the CLI component for a given manifest.
        The implementation will recursively discover children.
        """
        raise NotImplementedError

    def start(self, name: str):
        """
        Runs the command-line interface.
        """
        raise NotImplementedError 