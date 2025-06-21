# Pylium imports
from .types import ManifestTypes

# Standard library imports
from typing import ClassVar, List, Optional, Any, Callable, Dict, Annotated
from types import FunctionType
import importlib.machinery
import importlib.util
import pkgutil
import inspect
import sys

# External imports
from packaging.version import Version 
from pydantic import Field, computed_field, ConfigDict

# Logging
from logging import getLogger
logger = getLogger(__name__)


class Manifest(ManifestTypes.XObject, ManifestTypes):
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

    Now in the root "a", set __project_manifest__ = __manifest__, this marks the root
    manifest for the project.
    
    In the module "a.b", import the manifest from the root "a" and set
    __parent_manifest__ = __manifest__, this marks the parent manifest for the module.
    Create the __manifest__ for the module by calling __parent_manifest__.createChild(...),
    this creates a child manifest for the module.

    In the module "a.b.c", create the __manifest__ for the module by calling,
    do as above, __parent_manifest__ = __manifest__, __manifest__ = __parent_manifest__.createChild(...), 
    where parent is the manifest from the module "a.b".

    Define the class "D" with the manifest __manifest__ = __parent_manifest__.createChild(...),
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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Manifests own manifest
    # Usually here in header classes the manifest is defined
    __manifest__: ClassVar["Manifest"] = None
    ___root_manifest____: ClassVar["Manifest"] = None

    # Pydantic fields
    location: Optional[ManifestTypes.Location] = Field(default=None, description="Location information for this manifest")
    description: str = Field(default="", description="Description of this manifest")
    changelog: List[ManifestTypes.Changelog] = Field(default_factory=list, description="List of changelog entries")
    dependencies: List[ManifestTypes.Dependency] = Field(default_factory=list, description="List of dependencies")
    authors: ManifestTypes.AuthorList = Field(default_factory=lambda: ManifestTypes.AuthorList([]), description="List of authors")
    maintainers: Optional[ManifestTypes.MaintainerList] = Field(default=None, description="List of maintainers")
    copyright: Optional[ManifestTypes.Copyright] = Field(default=None, description="Copyright information")
    license: Optional[ManifestTypes.License] = Field(default=None, description="License information")
    status: ManifestTypes.Status = Field(default=ManifestTypes.Status.Development, description="Development status")
    accessMode: ManifestTypes.AccessMode = Field(default=ManifestTypes.AccessMode.Sync, description="Access mode")
    aiAccessLevel: ManifestTypes.AIAccessLevel = Field(default=ManifestTypes.AIAccessLevel.All, description="AI access level")
    threadSafety: ManifestTypes.ThreadSafety = Field(default=ManifestTypes.ThreadSafety.Unsafe, description="Thread safety level")
    frontend: ManifestTypes.Frontend = Field(default=ManifestTypes.Frontend.NoFrontend, description="Frontend type")
    backend: Optional[ManifestTypes.Backend] = Field(default=None, description="Backend type")
    additionalInfo: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @classmethod
    def func(cls, manifest: "Manifest") -> Callable:
        """
        Decorator to attach a Manifest to a function.
        Automatically sets ManifestLocation based on the function's definition.
        """
        def decorator(func: FunctionType) -> FunctionType:
            # Auto-fill location if not already set
            if manifest.location is None:
                # Check if function is a method by looking at the qualname
                classname = None
                if hasattr(func, '__qualname__') and '.' in func.__qualname__:
                    # It's a method, get the class name
                    classname = func.__qualname__.split(".")[0]
                    #print(f"  METHOD: {func.__qualname__} {classname}")
                    #manifest.location = Manifest.Location(module=func.__module__, classname=classname, funcname=func.__name__)
                #else:
                    # It's a regular function, explicitly set classname to None
                manifest.location = Manifest.Location(module=func.__module__, classname=classname, funcname=func.__name__)

            # Attach manifest
            #print(f"  ATTACHING MANIFEST: {manifest.location.fqnShort}")
            func.__manifest__ = manifest
            return func
        return decorator


    @classmethod
    def getManifest(cls, path: Optional[str] = None, search_base: Optional["Manifest"] = None) -> "Manifest":
        current_manifest = search_base if search_base else Manifest.___root_manifest____
        if not path:
            return current_manifest
        
        object_path_parts = path.split(".")
        current_path = ""

        for part in object_path_parts:
            current_path += f".{part}" if current_path else part
            # Search in children, not attributes
            found = None
            for child in current_manifest.children:
                if (child.location.fqnShort == current_path):
                    found = child
                    break
            if not found:
                print(f"  MANIFEST NOT FOUND: {current_path}")
                return None
            current_manifest = found
       
        return current_manifest


    def __init__(self,
                location: ManifestTypes.Location,
                description: str = "",
                changelog: Optional[List[ManifestTypes.Changelog]] = None, 
                dependencies: Optional[List[ManifestTypes.Dependency]] = None, 
                authors: Optional[ManifestTypes.AuthorList] = None,
                maintainers: Optional[ManifestTypes.MaintainerList] = None,
                copyright: Optional[ManifestTypes.Copyright] = None,
                license: Optional[ManifestTypes.License] = None,
                status: ManifestTypes.Status = ManifestTypes.Status.Development,
                accessMode: ManifestTypes.AccessMode = ManifestTypes.AccessMode.Sync,
                aiAccessLevel: Optional[ManifestTypes.AIAccessLevel] = ManifestTypes.AIAccessLevel.All,
                threadSafety: Optional[ManifestTypes.ThreadSafety] = ManifestTypes.ThreadSafety.Unsafe,
                frontend: Optional[ManifestTypes.Frontend] = ManifestTypes.Frontend.NoFrontend,
                backend: Optional[ManifestTypes.Backend] = ManifestTypes.Backend.NoBackend,
                *args, 
                **kwargs):
        """Initialize a new Manifest instance."""
        # Initialize Pydantic model with all fields
        super().__init__(
            location=location,
            description=description,
            changelog=changelog if changelog is not None else [],
            dependencies=dependencies if dependencies is not None else [],
            authors=authors if authors is not None else ManifestTypes.AuthorList([]),
            maintainers=maintainers if maintainers is not None else None,  # Will use authors if None
            copyright=copyright,
            license=license,
            status=status,
            accessMode=accessMode,
            aiAccessLevel=aiAccessLevel,
            threadSafety=threadSafety,
            frontend=frontend,
            backend=backend,
            additionalInfo=kwargs
        )
        
        # Set maintainers to authors if not provided
        if self.maintainers is None:
            self.maintainers = self.authors

    @computed_field
    @property
    def objectType(self) -> ManifestTypes.ObjectType:
        """Determine the object type based on the location."""
        object_type = ManifestTypes.ObjectType.Invalid
        if self.location:
            if self.location.isPackage:
                object_type = Manifest.ObjectType.Package
            elif self.location.isModule:
                object_type = Manifest.ObjectType.Module
            elif self.location.isClass:
                object_type = Manifest.ObjectType.Class
            elif self.location.isMethod:
                object_type = Manifest.ObjectType.Method
            elif self.location.isFunction:
                object_type = Manifest.ObjectType.Function
        return object_type
    

    @computed_field
    @property
    def isRoot(self) -> bool:
        """Check if the location points to the root manifest."""
        return isinstance(self, RootManifest)


    @computed_field
    @property
    def parent(self) -> Optional["Manifest"]:
        """
        Dynamically determine the parent manifest based on the location.
        For module manifests, looks for parent module's manifest.
        For class manifests, looks for containing module's manifest.
        """
        if not self.location or not self.location.module:
            return None

        if self.location.isFunction:
            # For function manifests, parent is the class or module manifest
            try:                
                module = importlib.import_module(self.location.module)
                if self.location.isMethod:                    
                    my_class = getattr(module, self.location.classname)
                    return getattr(my_class, "__manifest__", None)                    
                else:
                    return getattr(module, "__manifest__", None)
            except ImportError:
                return None

        # For class manifests, parent is the module manifest
        elif self.location.isClass:
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
            # First try to catch __parent_manifest__ in the module
            try:
                parent = importlib.import_module(self.location.module)
                return getattr(parent, "__parent_manifest__", None)
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

        print(f"  PARENT: {self.location.fqn} is not found")

        return None

    @computed_field
    @property
    def children(self) -> List["Manifest"]:
        """
        Return a list of direct child manifests.
        
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
            #print(f"  IMPORTING: {self.location.fqnShort}")
            #print(f"  IMPORTING: {self.location.module}")
            module = importlib.import_module(self.location.shortName)

            if self.location.isModule and self.location.isPackage:
                # We need to find all the __header__ and *_h submodules
                for finder, name, ispkg in pkgutil.iter_modules(module.__path__):
                    header : str = None
                    if ispkg:
                        # its a package, find the __header__ submodule  
                        header = f"{module.__name__}.{name}.__header__"

                    elif name.endswith("_h"):
                        header = f"{module.__name__}.{name}"

                    if header:
                        try:
                            importlib.import_module(header)
                        except ImportError as e:
                            pass                    

                #print(f"  MODULE: {self.location.fqnShort}")
                for name, member in inspect.getmembers(module):
                    if name.startswith("__") and name.endswith("__"):
                        continue
                    #print(f"  NAME: {name} {member}")
                    if hasattr(member, "__manifest__"):
                        
                        #print(f"  MANIFEST: {member.__manifest__.location.fqnShort}")
                        if member.__manifest__.parent == self and not member.__manifest__ in childs:
                            #print(f"ADD_MOD: {member.__manifest__.location.fqnShort}")
                            childs.append(member.__manifest__)
            
            elif self.location.isClass:
                #print(f"  SELF: {self.location.fqnShort}")
                my_class = getattr(module, self.location.classname)
                if hasattr(my_class, "__manifest__"):                    
                    for name, member in inspect.getmembers(my_class):
                        if name.startswith("__") and name.endswith("__"):
                            continue
                        #print(f"  NAME: {name}")
                        if hasattr(member, "__manifest__"):
                            #print(f"XNAME: {name}  MANIFEST: {member.__manifest__.location.fqnShort} PARENT: {member.__manifest__.parent.location.fqn}")
                            if member.__manifest__.parent == self and not member.__manifest__ in childs:
                                #print(f"ADD_CLASS: {member.__manifest__.location.fqnShort}")
                                childs.append(member.__manifest__)
            
            elif self.location.isFunction:
                #print(f"  SELF: {self.location.fqnShort} {self.objectType.name.upper()}")
                # Function dont have childs
                pass

        except ImportError as e:
            print(f"  IMPORT ERROR: {self.location.fqnShort} {e}")
            pass      

        #print(f"  CHILDREN: {childs}")

        return childs

    @computed_field
    @property
    def project(self) -> Optional["Manifest"]:
        """
        Get the project manifest (root manifest for the project).
        It is the module that has __project_manifest__ in its header.
        """
        mod = self        
        while mod is not None:
            # Check if my own module has __project_manifest__
            if hasattr(importlib.import_module(mod.location.module), "__project_manifest__"):
                return mod
            # If not, check if my parent has __project_manifest__
            mod = mod.parent
        return None

    @computed_field
    @property
    def contributors(self) -> ManifestTypes.ContributorList:
        """Get a list of all contributors from authors, maintainers, and changelog entries."""
        _contributors = set()  # Using a set to store authors to avoid duplicates
        if self.authors:
            for author in self.authors:
                _contributors.add(author)
        if self.maintainers:
            for maintainer in self.maintainers:
                _contributors.add(maintainer)
        if self.changelog:
            for entry in self.changelog:
                if entry.author:
                    _contributors.add(entry.author)  # Add author from changelog
        return Manifest.ContributorList(list(_contributors)) 

    @computed_field
    @property
    def version(self) -> Version:
        """Get the current version from the latest changelog entry."""
        if self.changelog and self.changelog[0].version:
            return self.changelog[0].version
        raise ValueError("Version not found in changelog")

    @computed_field
    @property
    def author(self) -> str:
        """Get the name of the first author if available."""
        if self.authors and len(self.authors) > 0:
            return self.authors[0].name
        return ""

    @computed_field
    @property
    def maintainer(self) -> str:
        """Get the name of the first maintainer if available."""
        if self.maintainers and len(self.maintainers) > 0:
            return self.maintainers[0].name
        return ""

    @computed_field
    @property
    def email(self) -> str:
        """Get the email of the first author if available."""
        if self.authors and len(self.authors) > 0 and self.authors[0].email:
            return self.authors[0].email
        return ""

    @computed_field
    @property
    def credits(self) -> List[str]:
        """Get a list of all author names."""
        return [author.name for author in self.authors]

    @computed_field
    @property
    def created(self) -> Optional[ManifestTypes.Date]:
        """Get the creation date from the last changelog entry."""
        if self.changelog:
            # Assuming the last entry in the changelog is the creation date
            return self.changelog[-1].date
        return None

    @computed_field
    @property
    def updated(self) -> Optional[ManifestTypes.Date]:
        """Get the last update date from the first changelog entry."""
        if self.changelog:
            # Assuming the first entry in the changelog is the last update date
            return self.changelog[0].date
        return None

    @computed_field
    @property
    def doc(self) -> str:
        """Get a basic documentation string."""
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
                   location: ManifestTypes.Location,
                   description: Optional[str] = None,
                   changelog: Optional[List[ManifestTypes.Changelog]] = None,
                   dependencies: Optional[List[ManifestTypes.Dependency]] = None,
                   authors: Optional[ManifestTypes.AuthorList] = None,
                   maintainers: Optional[ManifestTypes.MaintainerList] = None,
                   copyright: Optional[ManifestTypes.Copyright] = None,
                   license: Optional[ManifestTypes.License] = None,
                   status: Optional[ManifestTypes.Status] = None,
                   accessMode: Optional[ManifestTypes.AccessMode] = None,
                   threadSafety: Optional[ManifestTypes.ThreadSafety] = None,
                   frontend: Optional[ManifestTypes.Frontend] = ManifestTypes.Frontend.NoFrontend,
                   backend: Optional[ManifestTypes.Backend] = None,
                   aiAccessLevel: Optional[ManifestTypes.AIAccessLevel] = None) -> "Manifest":
        """
        Creates a new Manifest instance that inherits attributes from this (parent) manifest.
        Attributes that are explicitly provided to createChild will override the parent's attributes.
        For list-like attributes (changelog, dependencies), the provided value replaces the parent's, it's not merged.
        If None is provided for an attribute, it inherits from the parent.
        """
        return Manifest(
            location=location,
            description=description,
            changelog=changelog,
            dependencies=dependencies,
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
    
class RootManifest(Manifest):
    """
    The root manifest is the root manifest for everything.
    Create top level children from this manifest.
    """
    # No additional fields needed for RootManifest, it inherits all fields from Manifest
    
    def __init__(self, *args, **kwargs):
        """Initialize a new RootManifest instance."""
        # Initialize base Manifest with all fields
        super().__init__(*args, **kwargs)
    
    @property
    def parent(self) -> Optional["Manifest"]:
        return None
    
    @property
    def children(self) -> List["Manifest"]:
        # We need to search for __project_manifest__ in all available modules
        # and return the manifest for the module that has __project_manifest__
        _children = []
        for module in sys.modules.values():
            # We only accept top level packages here to be listed under the root manifest
            if hasattr(module, "__project_manifest__") and not "." in module.__name__:
                _children.append(module.__project_manifest__)
        return _children