from pylium import __project_manifest__ as __parent_manifest__
from pylium.manifest import Manifest

__manifest__ : Manifest = Manifest(
    parent=__parent_manifest__,
    location=Manifest.Location(module=__name__, classname=None), 
    description="The core functionalities of the Pylium library.",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025, 5, 28), 
                           author=__parent_manifest__.authors.rraudzus,
                           notes=["Initial definition of pylium.core package manifest."]),
        Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025, 5, 28), 
                           author=__parent_manifest__.authors.rraudzus,
                           notes=["Moved manifest definition to __header__.py"]),
        Manifest.Changelog(version=Manifest.Version("0.1.2"), date=Manifest.Date(2025, 6, 8),
                           author=__parent_manifest__.authors.rraudzus,
                           notes=["Major CLI system architectural overhaul across core package",
                                  "Implemented tree-based CLI architecture replacing dynamic class building",
                                  "Added comprehensive recursive navigation support with consistent behavior",
                                  "Enhanced manifest resolution supporting both flat and nested file patterns",
                                  "Improved CLI categorization (CLASS, COMMANDS, SUBMODULES) with fire integration",
                                  "Unified CLI behavior between direct and recursive access patterns",
                                  "Established foundation for multi-frontend support (CLI, FastAPI, etc.)",
                                  "Enhanced Header class integration and discoverability in CLI tree"]),
    ]
)





