from pylium.core import __manifest__ as __parent__
from pylium.core.header import Manifest, Header
from pylium.core.frontend import Frontend

from typing import ClassVar

__manifest__: Manifest = __parent__.createChild(
    location=Manifest.Location(module=__name__, classname=None),
    description="CLI module",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    dependencies=[ Manifest.Dependency(name="fire", version="0.7.0", type=Manifest.DependencyType.PIP, source="git+https://github.com/Verlusti/python-fire.git", category=Manifest.Dependency.Category.RUNTIME) ],
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,6,6), author=__parent__.authors.rraudzus, 
                                 notes=["Initial release"]),
        Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,6,6), author=__parent__.authors.rraudzus, 
                                 notes=["Added __manifest__ for module"]),
        Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,6,8), author=__parent__.authors.rraudzus,
                                 notes=["Complete architectural overhaul to tree-based CLI system",
                                        "Implemented CommandNode and CommandTree classes for canonical command structure",
                                        "Added CLIRenderer for python-fire frontend compatibility",
                                        "Support for both flat (module_h.py) and nested (module/__header__.py) file patterns",
                                        "Fixed manifest resolution to prefer header manifests over module manifests",
                                        "Implemented proper visibility checking for locally defined vs imported classes",
                                        "Added categorization support (CLASS, COMMANDS, SUBMODULES) with fire categories",
                                        "Ensured recursive CLI calls behave identically to direct module calls"]),
        Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,6,11), author=__parent__.authors.rraudzus,
                                 notes=["Added __parent__ to the cli module manifest to allow for proper manifest resolution"]),
        Manifest.Changelog(version="0.1.4", date=Manifest.Date(2025,6,20), author=__parent__.authors.rraudzus,
                                 notes=["Added make_function_wrapper to CLIRenderer to allow for proper function wrapping"]),
    ]
)

class CLI(Frontend):
    """
    A component that recursively builds and runs a command-line interface.
    """

    __manifest__ : Manifest = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="The core CLI building component for Pylium.",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.CLI,
        dependencies=[ Manifest.Dependency(name="fastapi", version="0.133.7", type=Manifest.DependencyType.PIP, category=Manifest.Dependency.Category.RUNTIME) ],
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,6,8), author=__parent__.authors.rraudzus,
                               notes=["Redesigned CLI class with tree-based architecture",
                                      "Replaced dynamic class building with CommandTree/CommandNode approach", 
                                      "Added support for recursive navigation with consistent behavior",
                                      "Enhanced manifest discovery for proper header resolution",
                                      "CLI now serves as frontend-agnostic command tree builder"]),
            Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,6,20), author=__parent__.authors.rraudzus,
                               notes=["Fixed critical bug in function wrapping using closure factory pattern",
                                      "Added make_function_wrapper to properly bind standalone functions",
                                      "Improved stability of CLI command routing",
                                      "Enhanced debugging capabilities with cleaner wrapper structure"])
        ]
    )

    frontendType : ClassVar[Manifest.Frontend] = Manifest.Frontend.CLI

    def __init__(self, manifest: Manifest, **kwargs):
        """
        Initializes the CLI component for a given manifest.
        The implementation will recursively discover children.
        """
        super().__init__(manifest=manifest, **kwargs)

# Register the CLI frontend to the Frontend registry
# This is done here to avoid circular imports
# Registration makes the frontend available to the Frontend.getFrontend() method
# so that the AppImpl can find the Frontend and instantiate it.
CLI.registerFrontend()

