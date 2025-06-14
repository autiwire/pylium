from typing import ClassVar, List, Optional, Any, Callable
from types import FunctionType
from packaging.version import Version 

import importlib.machinery
import importlib.util
import pkgutil
import inspect

from logging import getLogger
logger = getLogger(__name__)


class Manifest:
    """
    Metadata about a code unit (module, class, etc.).
    Can optionally include location information.
    
    Metadata includes:
    - Description and documentation
    - Version information and changelog
    - Authors and maintainers
    - Dependencies
    - License and copyright information
    - Optional: Location information (name, module, file, fqn)
    
    Manifests can be hierarchical:
    - Project manifest: Root manifest in __init__.py
    - Module manifest: One per module, inherits from project
    - Class manifest: Optional, for classes needing specific metadata
    
    Child manifests can be created using:
    manifest.createChild(location="new location") or
    Manifest.from_parent(parent_manifest, location="new location")
    
    ## Manifest Reference Patterns
    
    Three key patterns for referencing manifests in the hierarchy:

    Let there be a module called "a.b.c" with a class called "D" and a function "f",
    every module has a manifest, every class has a manifest, and functions can have manifests.

    The manifest for a module, class, or function is defined in the module or class header
    and called __manifest__.

    Now in the root "a", set __project__ = __manifest__, this marks the root
    manifest for the project.
    
    In the module "a.b", import the manifest from the root "a" and set
    __parent__ = __manifest__, this marks the parent manifest for the module.
    Create the __manifest__ for the module by calling __parent__.createChild(...),
    this creates a child manifest for the module.

    In the module "a.b.c", create the __manifest__ for the module by calling,
    do as above, __parent__ = __manifest__, __manifest__ = __parent__.createChild(...), 
    where parent is the manifest from the module "a.b".

    Define the class "D" with the manifest __manifest__ = __parent__.createChild(...),
    where parent is the manifest from the module "a.b.c".

    For functions, use the @Manifest.func decorator to attach a manifest:
    ```python
    # Simple pattern for regular functions
    @Manifest.func(Manifest(
        description="Function manifest example"
    ))
    def f():
        pass

    # Explicit pattern for implementation classes
    @Manifest.func(D.test.__manifest__)
    def test(self):
        print(f"Manifest: {self.__manifest__}")
    ```
    The function's manifest will automatically inherit from its containing class or module.
    For implementation classes, you can explicitly reference the manifest from the interface.

    This is how the manifest hierarchy is created and propagated through the
    modules, classes, and functions tree.
    
    This explicit pattern ensures AI-readable code and maintains clear separation
    between structural hierarchy and authorship/policy inheritance.
    """

    # Manifests own manifest
    # Usually here in header classes the manifest is defined
    __manifest__: ClassVar["Manifest"] = None

    from ._types import ManifestValue as Value
    from ._types import ManifestLocation as Location
    from ._types import ManifestAuthor as Author
    from ._types import ManifestAuthorList as AuthorList
    from ._types import ManifestMaintainerList as MaintainerList
    from ._types import ManifestContributorList as ContributorList
    from ._types import ManifestChangelog as Changelog
    from ._types import ManifestDependency as Dependency
    
    from ._license import ManifestCopyright as Copyright
    from ._license import ManifestLicense as License
    from ._license import ManifestLicenseList as LicenseList
    from ._license import licenses as licenses

    from ._enums import ManifestStatus as Status
    from ._enums import ManifestAccessMode as AccessMode
    from ._enums import ManifestThreadSafety as ThreadSafety

    from ._flags import ManifestFrontend as Frontend
    from ._flags import ManifestBackend as Backend
    from ._flags import ManifestBackendGroup as BackendGroup
    from ._flags import ManifestAIAccessLevel as AIAccessLevel

    Date = Value.Date


    @classmethod
    def func(cls, manifest: "Manifest") -> Callable:
        """
        Decorator to attach a Manifest to a function.
        Automatically sets ManifestLocation based on the function's definition.
        """
        def decorator(func: FunctionType) -> FunctionType:
            # Auto-fill location if not already set
            print(f"DEBUG: manifest.location: {manifest.location}") # DEBUG
            print(f"DEBUG: func: {func}") # DEBUG
            if manifest.location is None:
                classname = None
                if func.__qualname__:
                    classname = func.__qualname__.split(".")[0]
                manifest.location = Manifest.Location(module=func.__module__, classname=classname, funcname=func.__name__)

            # Attach manifest
            func.__manifest__ = manifest
            return func
        return decorator

    def __init__(self,
                location: Location,
                description: str = "",
                changelog: Optional[List[Changelog]] = None, 
                dependencies: Optional[List[Dependency]] = None, 
                authors: Optional[AuthorList] = None,
                maintainers: Optional[MaintainerList] = None,
                copyright: Optional[Copyright] = None,
                license: Optional[License] = None,
                status: Status = Status.Development,
                accessMode: AccessMode = AccessMode.Sync,
                aiAccessLevel: Optional[AIAccessLevel] = AIAccessLevel.All,
                threadSafety: Optional[ThreadSafety] = ThreadSafety.Unsafe,
                frontend: Optional[Frontend] = Frontend.NoFrontend,
                backend: Optional[Backend] = Backend.NoBackend,
                *args, 
                **kwargs):
        
        self.location = location
        self.description = description
        self.changelog = changelog if changelog is not None else []
        self.dependencies = dependencies if dependencies is not None else []
        self.authors = authors if authors is not None else Manifest.AuthorList([])
        self.maintainers = maintainers if maintainers is not None else self.authors # If maintainers not given, use authors
        self.copyright = copyright
        self.license = license if license is not None else self.licenses.NoLicense # Default to NoLicense
        self.status = status
        self.accessMode = accessMode
        self.threadSafety = threadSafety
        self.frontend = frontend
        self.backend = backend
        self.aiAccessLevel = aiAccessLevel if aiAccessLevel is not None else self.AIAccessLevel.NoAccess

        # Store any additional keyword arguments
        self.additionalInfo = kwargs

    @property
    def parent(self) -> Optional["Manifest"]:
        """
        Dynamically determines the parent manifest based on the location.
        For module manifests, looks for parent module's manifest.
        For class manifests, looks for containing module's manifest.
        """

        if not self.location:
            return None

        elif self.location.isFunction:
            # For function manifests, parent is the class manifest
            if self.location.isClass:
                try:
                    module = importlib.import_module(self.location.module)
                    return getattr(module, "__manifest__", None)
                except ImportError:
                    return None

        # For class manifests, parent is the module manifest
        if self.location.isClass:
            try:
                module = importlib.import_module(self.location.module)
                return getattr(module, "__manifest__", None)
            except ImportError:
                return None

        elif self.location.isModule:               
            # Special case for manifest module
            _manifest_module_shortname = ".".join(Manifest.__module__.split(".")[:-1])
            if self.location.shortName == _manifest_module_shortname:
                from pylium import __manifest__ as parent
                return parent
            
            # For module manifests, parent is the parent module
            # First try to catch __parent__ in the module
            try:
                parent = importlib.import_module(self.location.module)
                return getattr(parent, "__parent__", None)
            except ImportError:
                pass

            # If not found, try to find the parent module via path
            module_parts = self.location.shortName.split(".")
            if len(module_parts) > 1:
                parent_module = ".".join(module_parts[:-1])
                try:
                    parent = importlib.import_module(parent_module)
                    return getattr(parent, "__manifest__", None)
                except ImportError:
                    return None

        return None

    @property
    def children(self) -> List["Manifest"]:
        """
        Returns a list of direct child manifests.
        
        The manifest hierarchy is defined by parent-child relationships:
        
        Root Manifest (special case):
        - Has no parent
        - Can have any type of child
        
        Module Manifest:
        - Can be parent to other modules (creating levels/hierarchy)
        - Can have classes and functions as children
        - Example: pylium.core manifest can be parent to pylium.core.cli manifest
        
        Class Manifest:
        - Can have functions as children
        - Example: A class in pylium.core.cli can have function manifests
        
        Function Manifest:
        - Leaf node
        - No children
        
        The hierarchy is:
        Root
        └── Module (level 1)
            ├── Module (level 2)
            │   ├── Class
            │   │   └── Function
            │   └── Function
            ├── Class
            │   └── Function
            └── Function
        """
    
        childs = []
        
        try:
            # Only look in the current module, not recursively
            module = importlib.import_module(self.location.shortName)
            for name, obj in inspect.getmembers(module):
                child_manifest = None
                
                # Search module for child manifests of modules, classes and functions as it is a module
                if self.location.isModule:
                    if ((self.location.isPackage and inspect.ismodule(obj)) or inspect.isclass(obj)) and hasattr(obj, "__manifest__"):
                        child_manifest = obj.__manifest__

                # Search for child manifests of functions in class
                if self.location.isClass:
                    if inspect.isclass(obj) and hasattr(obj, "__manifest__"):
                        child_manifest = obj.__manifest__

                if child_manifest and child_manifest.parent == self and not child_manifest in childs:
                    #print(f"CHILD__: {child_manifest.location.shortName}")
                    childs.append(child_manifest)

        except ImportError:
            pass      

        return childs

    @property
    def __project__(self) -> Optional["Manifest"]:
        """
        The project manifest is the root manifest for the project.
        It is the module that has __project__ in its header.
        """
        mod = self        
        while mod is not None:
            # Check if my own module has __project__
            if hasattr(importlib.import_module(mod.location.module), "__project__"):
                return mod
            # If not, check if my parent has __project__
            mod = mod.parent
        return None

    @property
    def contributors(self) -> ContributorList:
        # We create a list of contributors from authors, maintainers, and changelog entries
        _contributors = set() # Using a set to store authors to avoid duplicates
        if self.authors:
            for author in self.authors:
                _contributors.add(author)
        if self.maintainers:
            for maintainer in self.maintainers:
                _contributors.add(maintainer)
        if self.changelog:
            for entry in self.changelog:
                if entry.author:
                    _contributors.add(entry.author) # Add author from changelog
        return Manifest.ContributorList(list(_contributors)) 

    @property
    def version(self) -> Version:
        if self.changelog and self.changelog[0].version:
            return Version(self.changelog[0].version)
        raise ValueError("Version not found in changelog")

    @property
    def author(self) -> str:
        # Returns the name of the first author if available
        if self.authors and len(self.authors) > 0:
            return self.authors[0].name
        return ""

    @property
    def maintainer(self) -> str:
        # Returns the name of the first maintainer if available
        if self.maintainers and len(self.maintainers) > 0:
            return self.maintainers[0].name
        return ""

    @property
    def email(self) -> str:
        # Returns the email of the first author if available
        if self.authors and len(self.authors) > 0 and self.authors[0].email:
            return self.authors[0].email
        return ""

    @property
    def credits(self) -> List[str]:
        # Returns a list of author names
        return [author.name for author in self.authors]

    @property
    def created(self) -> Optional[Date]:
        if self.changelog:
            # Assuming the last entry in the changelog is the creation date
            return self.changelog[-1].date
        return None

    @property
    def updated(self) -> Optional[Date]:
        if self.changelog:
            # Assuming the first entry in the changelog is the last update date
            return self.changelog[0].date
        return None

    @property
    def doc(self) -> str:
        # Basic documentation string, could be expanded
        parts = [self.description]
        if self.version:
            parts.append(f"Version: {self.version}")
        if self.authors:
            parts.append(f"Authors: {', '.join(author.name for author in self.authors)}")
        if self.maintainers:
            parts.append(f"Maintainers: {', '.join(maintainer.name for maintainer in self.maintainers)}")
        if self.license:
            parts.append(f"License: {self.license.name}")
        # Could add more details like dependencies, copyright, etc.
        return ". ".join(filter(None, parts)) + "."

    def __str__(self):
        return f"{self.location.fqn} (v{self.version if self.changelog else 'N/A'})"

    def __repr__(self):
        # Provides a more detailed representation, could be made even more exhaustive
        return f"Manifest({self.location.fqn}, version='{self.version if self.changelog else 'N/A'}', authors={len(self.authors) if self.authors else 0})"

    def __hash__(self):
        # Hash based on a few key identifying attributes
        # Note: Manifest is mutable, so hashing can be tricky if based on mutable fields.
        # Using location fqn as a primary key for the hash.
        return hash((self.location.fqn, str(self.version if self.changelog else None)))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return False
        # Compare based on key attributes for equality
        return (
            self.location.fqn == other.location.fqn and
            (self.version if self.changelog else None) == (other.version if other.changelog else None) and 
            self.description == other.description
        )

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) < (other.location.fqn, other.version if other.changelog else Version("0"))

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) <= (other.location.fqn, other.version if other.changelog else Version("0"))

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) > (other.location.fqn, other.version if other.changelog else Version("0"))

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) >= (other.location.fqn, other.version if other.changelog else Version("0"))

    def createChild(self, 
                   location: Location,
                   description: Optional[str] = None,
                   changelog: Optional[List[Changelog]] = None,
                   dependencies: Optional[List[Dependency]] = None,
                   authors: Optional[AuthorList] = None,
                   maintainers: Optional[MaintainerList] = None,
                   copyright: Optional[Copyright] = None,
                   license: Optional[License] = None,
                   status: Optional[Status] = None,
                   accessMode: Optional[AccessMode] = None,
                   threadSafety: Optional[ThreadSafety] = None,
                   frontend: Optional[Frontend] = None,
                   backend: Optional[Backend] = None,
                   aiAccessLevel: Optional[AIAccessLevel] = None) -> "Manifest":
        """
        Creates a new Manifest instance that inherits attributes from this (parent) manifest.
        Attributes that are explicitly provided to createChild will override the parent's attributes.
        For list-like attributes (changelog, dependencies), the provided value replaces the parent's, it's not merged.
        If None is provided for an attribute, it inherits from the parent.
        """
        return Manifest(
            location=location,
            description=description if description is not None else self.description,
            changelog=changelog if changelog is not None else self.changelog,
            dependencies=dependencies if dependencies is not None else self.dependencies,
            authors=authors if authors is not None else self.authors,
            maintainers=maintainers if maintainers is not None else self.maintainers,
            copyright=copyright if copyright is not None else self.copyright,
            license=license if license is not None else self.license,
            status=status if status is not None else self.status,
            accessMode=accessMode if accessMode is not None else self.accessMode,
            threadSafety=threadSafety if threadSafety is not None else self.threadSafety,
            frontend=frontend if frontend is not None else self.frontend,
            backend=backend if backend is not None else self.backend,
            aiAccessLevel=aiAccessLevel if aiAccessLevel is not None else self.aiAccessLevel
        )
    
 