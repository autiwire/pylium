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
import threading

# External imports
from packaging.version import Version 
from pydantic import Field, computed_field, ConfigDict

# Logging
from logging import getLogger
logger = getLogger(__name__)

# Import manifest header module at module level to avoid thread safety issues with imports
import pylium.manifest.__header__ as manifest_header_module


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
    __root_manifest__: ClassVar["Manifest"] = None

    # Pydantic fields
    location: Optional[ManifestTypes.Location] = Field(default=None, description="Location information for this manifest")
    description: str = Field(default="", description="Description of this manifest")
    changelog: List[ManifestTypes.Changelog] = Field(default_factory=list, description="List of changelog entries")
    dependencies: List[ManifestTypes.Dependency] = Field(default_factory=list, description="List of dependencies")
    authors: ManifestTypes.AuthorList = Field(default_factory=lambda: ManifestTypes.AuthorList(authors=[]), description="List of authors")
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
        current_manifest = search_base if search_base else Manifest.__root_manifest__
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
                parent: "Manifest",
                location: Optional[ManifestTypes.Location] = None,
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


        class CallerInfo:
            from types import FrameType

            def __init__(self, frame: FrameType):
                self.module_name: str = frame.f_globals.get('__name__', 'unknown')
                self.module: Optional[object] = sys.modules.get(self.module_name)
                self.function: str = frame.f_code.co_name
                self.qualname: str = frame.f_code.co_qualname

                self.classname: Optional[str] = None
                self.is_method: bool = False
                self.is_class_scope: bool = False
                self.is_module_scope: bool = self.qualname == "<module>"

                if "self" in frame.f_locals:
                    self.classname = type(frame.f_locals["self"]).__name__
                    self.is_method = True
                elif "cls" in frame.f_locals:
                    self.classname = frame.f_locals["cls"].__name__
                    self.is_method = True
                elif "__module__" in frame.f_locals:
                    # we're in a class body (definition time)
                    self.classname = self.qualname
                    self.is_class_scope = True

            def as_dict(self):
                return {
                    "module": self.module_name,
                    "class": self.classname,
                    "function": self.function,
                    "qualname": self.qualname,
                    "is_method": self.is_method,
                    "is_class_scope": self.is_class_scope,
                    "is_module_scope": self.is_module_scope,
                }

            def __str__(self):
                parts = [f"[{self.module_name}]"]
                if self.classname:
                    parts.append(f"class {self.classname}")
                if self.function and self.function != "<module>":
                    parts.append(f"def {self.function}()")
                return " → ".join(parts)


        frame = inspect.currentframe().f_back
        info = CallerInfo(frame)
        print(info)
        
        # --- Function ---
#        func_name = frame.f_code.co_name

        # --- Class ---
#        cls_name = None
        # Check if 'self' or 'cls' is in local variables
#        if 'self' in frame.f_locals:
#            cls_name = type(frame.f_locals['self']).__name__
#        elif 'cls' in frame.f_locals:
#            cls_name = frame.f_locals['cls'].__name__

#        print({
#            "module": frame.f_globals.get("__name__", None),
#            "function": frame.f_code.co_name,
#            "class": type(frame.f_locals.get("self", None)).__name__ if "self" in frame.f_locals else None,
#        })

        # Store basic info
        #self.description = description
        self._children = []
        self._children_lock = threading.Lock()
        
        #
        

        # Detect context and set pointer
        if 'locals' in frame.f_locals and '__module__' in frame.f_locals:
            # We're in a class definition
            print(f"  CLASS: {frame.f_code.co_name}")
#            self._context = 'class'

#            self._ptr = frame.f_locals['locals']  # The class being defined
            #self.fqn = f"{module_name}.{frame.f_code.co_name}"
            pass
            
        elif frame.f_code.co_name != '<module>':
            # We're in a function/method
#            self._context = 'function'
#            self._ptr = frame.f_code  # The function object
            
            # Get full qualified name including class if we're in a method
            if 'self' in frame.f_locals:
                #print(f"  METHOD: {frame.f_code.co_name}")
                #cls_name = frame.f_locals['self'].__class__.__name__
                #self.fqn = f"{module_name}.{cls_name}.{frame.f_code.co_name}"
                pass
            else:

                #self.fqn = f"{module_name}.{frame.f_code.co_name}"
                pass
                
        else:
            # We're at module level
#            self._context = 'module'
#            self._ptr = module
            #self.fqn = module_name
            pass

        # Inherit from parent if not provided
        if parent:
            #self.description = parent.description
            #self.changelog = parent.changelog
            #self.dependencies = parent.dependencies
            authors = parent.authors if authors is None else authors
            maintainers = parent.maintainers if maintainers is None else maintainers
            copyright = parent.copyright if copyright is None else copyright
            license = parent.license if license is None else license
            status = parent.status if status is None else status
            accessMode = parent.accessMode if accessMode is None else accessMode
            aiAccessLevel = parent.aiAccessLevel if aiAccessLevel is None else aiAccessLevel
            threadSafety = parent.threadSafety if threadSafety is None else threadSafety
            frontend = parent.frontend if frontend is None else frontend
            backend = parent.backend if backend is None else backend


        # Initialize Pydantic model with all fields
        super().__init__(
            location=location,
            description=description,
            changelog=changelog if changelog is not None else [],
            dependencies=dependencies if dependencies is not None else [],
            authors=authors if authors is not None else ManifestTypes.AuthorList(authors=[]),
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
        
        self._parent_lock = threading.Lock()
        self._parent = parent


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
        return self._parent is None


    @computed_field
    @property
    def parent(self) -> Optional["Manifest"]:
        """
        Dynamically determine the parent manifest in a thread-safe manner.
        - Default is the private _parent field
        - Special case: manifest module uses __parent_manifest__
        
        Thread Safety:
        - Uses a class-level lock for parent resolution
        - Import of manifest_header_module is done at module level
        - Parent resolution is atomic
        """
        # Fast path - if parent is set, return it (no lock needed as it's immutable after init)
        if self._parent is not None:
            return self._parent

        # Slow path - resolve parent with proper locking
        with self._parent_lock:
            # Check again in case another thread set it while we were waiting
            if self._parent is not None:
                return self._parent
                
            # Check if this is the manifest module's manifest
            if self == manifest_header_module.__manifest__:
                # Get parent manifest atomically under the lock
                self._parent = getattr(manifest_header_module, "__parent_manifest__", None)
                return self._parent
            
            return None

    @computed_field
    @property
    def parent_bak(self) -> Optional["Manifest"]:
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

        #print(f"  PARENT: {self.location.fqn} is not found")

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
        
        if self.isRoot:
            for module in sys.modules.values():
                # We only accept top level packages here to be listed under the root manifest
                if hasattr(module, "__project_manifest__") and not "." in module.__name__:
                    childs.append(module.__project_manifest__)
            return childs

        try:
            # Only look in the current module, not recursively
            #print(f"  IMPORTING: {self.location.fqnShort}")
            #print(f"  IMPORTING: {self.location.module}")
            module = importlib.import_module(self.location.shortName)

            if self.location.isModule and self.location.isPackage:
                # We need to find all the __header__ and *_h submodules
                for finder, name, ispkg in pkgutil.iter_modules(module.__path__):
                    #print(f"  FINDER: {finder} {name} {ispkg}")
                    header : str = None
                    if ispkg:
                        # its a package, find the __header__ submodule  
                        header = f"{module.__name__}.{name}.__header__"

                    elif name.endswith("_h"):
                        header = f"{module.__name__}.{name}"

                    if header:
                        try:
                            #print(f"  IMPORTING_HEADER: {header}")
                            importlib.import_module(header)
                        except ImportError as e:
                            #print(f"  IMPORT ERROR: {e}")
                            pass                    

                #print(f"  MODULE: {self.location.fqnShort}")
                for name, member in inspect.getmembers(module):
                    if name.startswith("__") and name.endswith("__"):
                        continue
                    #print(f"  NAME: {name} {member}")
                    if hasattr(member, "__manifest__"):
                        
                        #print(f"  MANIFEST: {member.__manifest__}")
                        #print(f"  PARENT: {member.__manifest__.parent}")
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
        #print(f"  TYPE: {type(self)} == {type(other)}")
        
        # If one is root manifest, the other must be too
        if self.isRoot != other.isRoot:
            return False

        # root-manifest is a special case, there can be only one root-manifest
        if self.isRoot:
            return True 

        # For normal manifests
        if not isinstance(other, Manifest):
            return False

        #print(f"  LOC: {self.location} == {other.location}")

        # Both must have a location
        if self.location is None or other.location is None:
            return False

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


    def _get_dependencies_recursive(self, recursive: bool = True, type_filter: str = None, category_filter: str = None) -> Dict[str, List[ManifestTypes.Dependency]]:
        """
        Get the dependencies of the given object path
        """

        dependencies = {}

        if recursive:
            for child in self.children:
                dependencies.update(child._get_dependencies_recursive(recursive, type_filter, category_filter))

        # Add self to the dependencies if we have elements
        if len(self.dependencies) > 0:
            # Root manifest is purely virtual, so it has no location
            if self.isRoot:
                dependencies.update({"/": self.dependencies})
            else:
                dependencies.update({self.location.fqnShort: self.dependencies})

        # Filter dependencies based on type and category
        filtered_dependencies = {}
        for module, deps in dependencies.items():
            filtered_deps = []
            for dep in deps:
                # Case insensitive comparison for both filters
                dep_type = dep.type.name.upper()
                dep_category = getattr(dep, 'category', None) and getattr(dep, 'category').name.upper()
                type_match = type_filter is None or dep_type == type_filter.upper()
                category_match = category_filter is None or (dep_category and dep_category == category_filter.upper())
                
                if type_match and category_match:
                    filtered_deps.append(dep)
            if filtered_deps:
                filtered_dependencies[module] = filtered_deps

        return filtered_dependencies


    def listDependencies(self, recursive: bool = True, type_filter: str = None, category_filter: str = None) -> ManifestTypes.Dependency.List:
        """
        Get the dependencies of the given object path
        """
        dependencies = self._get_dependencies_recursive(recursive, type_filter, category_filter)
        return Manifest.Dependency.List(dependencies=dependencies)

