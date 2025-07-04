# Note: This is a special case in the header/impl pattern:
# Usually __impl__.py would import from __header__.py, but here it's reversed because:
# 1. The Manifest class is the core implementation that doesn't know about headers
# 2. The header needs the Manifest class to define its own manifest
# 3. This creates a clean separation where Manifest remains independent of the header concept
# 4. Yet the manifest system still benefits from the recursive structure through __manifest__ and parent resolution
from .__impl__ import Manifest


from typing import Dict, Callable


# Core authors for use in own manifest
_manifest_core_authors = Manifest.AuthorList(authors=[
    Manifest.Author(
        tag="rraudzus", 
        name="Rouven Raudzus", 
        email="raudzus@autiwire.org", 
        company="AutiWire GmbH", 
        since_version=Manifest.Version("0.0.0"), 
        since_date=Manifest.Date(2025,5,10)
    )
])    

# Core maintainers, initially same as authors
_manifest_core_maintainers = Manifest.AuthorList(authors=_manifest_core_authors.authors.copy())

# Root manifest for the manifest system
__root_manifest__ = Manifest(
    parent=None,
    location=Manifest.Location(module="", classname=None),
    description="Root manifest for the manifest system",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.NoFrontend,
    aiAccessLevel=Manifest.AIAccessLevel.Read,
    dependencies=[],
    authors=_manifest_core_authors,
    maintainers=_manifest_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,6,16), author=_manifest_core_authors.rraudzus),
    license=Manifest.Licenses.NoLicense,
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,6,16), author=_manifest_core_authors.rraudzus, 
                            notes=["Initial release"]),
    ]
)

Manifest.__root_manifest__ = __root_manifest__

__parent_manifest__ = None # Special case for the manifests module, set externally (in manifest parent modules __header__.py)

# Define Manifests own manifest (per-module-manifest)
__manifest__ = Manifest(
    parent=__parent_manifest__,
    location=Manifest.Location(module=__name__, classname=None),
    description="Base class for all manifests",    
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    aiAccessLevel=Manifest.AIAccessLevel.Read,
    dependencies=[ 
        Manifest.Dependency(name="packaging", version=Manifest.Version(">=25.0.0"), type=Manifest.Dependency.Type.PIP, category=Manifest.Dependency.Category.RUNTIME),
        Manifest.Dependency(name="pydantic", version=Manifest.Version(">=2.11.4"), type=Manifest.Dependency.Type.PIP, category=Manifest.Dependency.Category.RUNTIME)
    ],
    authors=_manifest_core_authors,
    maintainers=_manifest_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus),
    license=Manifest.Licenses.NoLicense,
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus, 
                            notes=["Initial release"]),
        Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025,5,19), author=_manifest_core_authors.rraudzus, 
                            notes=["Added maintainers"]),
        Manifest.Changelog(version=Manifest.Version("0.1.2"), date=Manifest.Date(2025,5,20), author=_manifest_core_authors.rraudzus, 
                            notes=["Added license"]),
        Manifest.Changelog(version=Manifest.Version("0.1.3"), date=Manifest.Date(2025,5,21), author=_manifest_core_authors.rraudzus, 
                            notes=["Modified location information, requires less parameters"]),
        Manifest.Changelog(version=Manifest.Version("0.1.4"), date=Manifest.Date(2025,5,22), author=_manifest_core_authors.rraudzus, 
                            notes=["Moved _manifest_core_* from class to module for more compactness"]),
        Manifest.Changelog(version=Manifest.Version("0.1.5"), date=Manifest.Date(2025,5,23), author=_manifest_core_authors.rraudzus,
                            notes=["Added doc property to get the docstring of the class or module"]),
        Manifest.Changelog(version=Manifest.Version("0.1.6"), date=Manifest.Date(2025,5,27), author=_manifest_core_authors.rraudzus, 
                            notes=["Added per-module-manifest"]),
        Manifest.Changelog(version=Manifest.Version("0.1.7"), date=Manifest.Date(2025,5,28), author=_manifest_core_authors.rraudzus, 
                            notes=["Moved pylium.core.manifest to pylium.manifest"]),
        Manifest.Changelog(version=Manifest.Version("0.1.8"), date=Manifest.Date(2025,5,28), author=_manifest_core_authors.rraudzus, 
                            notes=["Added ai_access_level to manifest"]),
        Manifest.Changelog(version=Manifest.Version("0.1.9"), date=Manifest.Date(2025,5,28), author=_manifest_core_authors.rraudzus, 
                            notes=["Set manifest ai_access_level to read"]),
        Manifest.Changelog(version=Manifest.Version("0.1.10"), date=Manifest.Date(2025,5,29), author=_manifest_core_authors.rraudzus, 
                            notes=["Added license tag to manifest"]),
        Manifest.Changelog(version=Manifest.Version("0.1.11"), date=Manifest.Date(2025,5,29), author=_manifest_core_authors.rraudzus, 
                            notes=["Set manifest license to Apache2"]),
        Manifest.Changelog(version=Manifest.Version("0.1.12"), date=Manifest.Date(2025,6,13), author=_manifest_core_authors.rraudzus,
                            notes=["Enhanced function manifest support",
                                   "Added @func decorator for attaching manifests to functions",
                                   "Improved manifest location handling for functions",
                                   "Added type detection for module, class, function, and method locations"]),
        Manifest.Changelog(version=Manifest.Version("0.1.13"), date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                            notes=["Moved to header/impl design",
                                   "Added parent property to manifest"]),
        Manifest.Changelog(version=Manifest.Version("0.1.14"), date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                            notes=["Improved manifest parent resolution",
                                   "Added special case for manifest module parent",
                                   "Fixed circular import issues",
                                   "Moved types to _types.py",
                                   "Moved enums to _enums.py",
                                   "Moved license to _license.py",
                                   "Moved flags to _flags.py",
                                   "Created __header__.py from __init__.py contents",
                                   "Reduced __init__.py to minimal interface"]),
        Manifest.Changelog(version=Manifest.Version("0.1.15"), date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                             notes=["Added documentation for function manifest patterns",
                                   "Added examples for both simple and implementation class function manifests"]),
        Manifest.Changelog(version=Manifest.Version("0.1.16"), date=Manifest.Date(2025,6,20), author=_manifest_core_authors.rraudzus,
                             notes=["Integrated Pydantic for enhanced type validation and serialization",
                                   "Added proper Pydantic fields to all manifest types",
                                   "Converted Version type to use Pydantic validation",
                                   "Updated dependency types to use Pydantic fields",
                                   "Enhanced type safety across the manifest system"]),
        Manifest.Changelog(version=Manifest.Version("0.1.17"), date=Manifest.Date(2025,6,21), author=_manifest_core_authors.rraudzus,
                             notes=["Improved JSON serialization using Pydantic's native capabilities",
                                   "Converted dependency enums to str-based Enums for better serialization",
                                   "Removed custom JSON serialization in favor of Pydantic's model_dump_json",
                                   "Enhanced equality and hash operations for dependency types"]),
        Manifest.Changelog(version=Manifest.Version("0.1.18"), date=Manifest.Date(2025,6,22), author=_manifest_core_authors.rraudzus,
                             notes=["Added dependency conflict detection and reporting",
                                   "Enhanced dependency version comparison logic",
                                   "Added deps function to create a dependency list from the given object path"])
    ]
)

# Define Manifests own manifest (per-class-manifest)
Manifest.__manifest__ = Manifest(
    parent=__manifest__,
    location=Manifest.Location(module=__name__, classname=Manifest.__qualname__),
    description="Base class for all manifests",    
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.NoFrontend,
    aiAccessLevel=Manifest.AIAccessLevel.Read,
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus, 
                          notes=["Initial release"]),
        Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025,5,19), author=_manifest_core_authors.rraudzus, 
                          notes=["Added per-class-manifest"]),
        Manifest.Changelog(version=Manifest.Version("0.1.2"), date=Manifest.Date(2025,6,7), author=_manifest_core_authors.rraudzus, 
                          notes=["Added shortName property to manifest class"]),
        Manifest.Changelog(version=Manifest.Version("0.1.3"), date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                          notes=["Added children property for manifest hierarchy traversal",
                                "Implemented efficient child manifest discovery",
                                "Supports module, class, and function child manifests"]),
        Manifest.Changelog(version=Manifest.Version("0.1.4"), date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                          notes=["The frontend now is set to NoFrontend by default instead of inheriting from parent"]),
        Manifest.Changelog(version=Manifest.Version("0.1.5"), date=Manifest.Date(2025,6,20), author=_manifest_core_authors.rraudzus,
                          notes=["Added dependency category to manifest",
                                 "Added dependency direction to manifest"]),
        Manifest.Changelog(version=Manifest.Version("0.1.6"), date=Manifest.Date(2025,6,20), author=_manifest_core_authors.rraudzus,
                          notes=["Integrated Pydantic model system",
                                 "Enhanced field validation and type safety",
                                 "Added proper serialization support"]),
        Manifest.Changelog(version=Manifest.Version("0.1.7"), date=Manifest.Date(2025,6,21), author=_manifest_core_authors.rraudzus,
                          notes=["Improved JSON serialization using native Pydantic methods",
                                 "Enhanced type safety for dependency enums",
                                 "Optimized serialization performance"]),
        Manifest.Changelog(version=Manifest.Version("0.1.8"), date=Manifest.Date(2025,6,22), author=_manifest_core_authors.rraudzus,
                          notes=["Added dependency conflict detection and reporting",
                                 "Enhanced dependency version comparison logic",
                                 "Improved dependency conflict resolution"]),
        Manifest.Changelog(version=Manifest.Version("0.1.9"), date=Manifest.Date(2025,6,23), author=_manifest_core_authors.rraudzus,
                          notes=["Added tree function to print the manifest tree",
                                 "Added deps function to create a dependency list from the given object path"])
    ]
)


@Manifest.func(Manifest(
    parent=__manifest__,
    location=None,
    description="Prints the manifest tree",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    aiAccessLevel=Manifest.AIAccessLevel.Read,
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,6,17), author=_manifest_core_authors.rraudzus, 
                            notes=["Added tree function to print the manifest tree"]),
    ]
))
def tree(object: str = "", simple: bool = False, indent: int = 0):
    """Prints the manifest tree.
    
    The object can be a module, class, method or function.

    Args:
        object: Object to print the tree for
        simple: If True, print only the object name
        indent: Indentation level
    """

    from pylium.core.app import App
    from ._cli import cli_tree

    # TODO: Add a way to print the tree for a specific object     

    frontend_funcs : Dict[Manifest.Frontend, Callable] = { Manifest.Frontend.NoFrontend: None,
                                                            Manifest.Frontend.CLI: cli_tree }

    frontend_type = App.default.frontend.frontendType
    if frontend_type is not None and frontend_type in frontend_funcs.keys():
        frontend_funcs[frontend_type](Manifest.getManifest(object), simple, indent)
    else:
        raise RuntimeError("No frontend function available")


@Manifest.func(Manifest(
    parent=__manifest__,
    location=None,
    description="Creates a dependency list from the given object path",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    aiAccessLevel=Manifest.AIAccessLevel.Read,
    changelog=[
        Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,6,22), author=_manifest_core_authors.rraudzus, 
                            notes=["Added deps function to create a dependency list from the given object path"]),
    ]
))
def deps(object: str = "", recursive: bool = True, type_filter: str = None, category_filter: str = None) -> Manifest.Dependency.List:
    """Creates a dependency list from the given object path.
    
    The object can be a module, class, method or function.

    Args:
        object: Object to create a dependency list for
        recursive: Whether to include recursive dependencies
        type_filter: Filter by dependency type
        category_filter: Filter by dependency category

        Returns:
        Manifest.Dependency.List object containing:
        - dependencies: Dict[str, List[Manifest.Dependency]] - All dependencies per module
        - conflicts: List[Manifest.Dependency.Conflict] - All detected conflicts
        - stats: Manifest.Dependency.Stats - Statistics about dependencies
    """

    return Manifest.Dependency.List.fromManifest(object, recursive, type_filter, category_filter)

