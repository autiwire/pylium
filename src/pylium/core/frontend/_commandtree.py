from pylium.core import __manifest__ as __parent__
from pylium.core.header import Manifest, Header

from typing import ClassVar, Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

__manifest__ : Manifest = __parent__.createChild(
    location=Manifest.Location(module=__name__, classname=None),
    description="Command tree builder module",
    status=Manifest.Status.Development,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,6,13), author=__parent__.authors.rraudzus,
                                 notes=["Initial release"]),
    ]
)


class CommandTree(Header):
    """Builds and manages the command tree structure."""
    
    __manifest__ : Manifest = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="Command tree builder class",
        status=Manifest.Status.Development,
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,6,13), author=__parent__.authors.rraudzus,
                                 notes=["Initial release"]),
        ]
    )

    class Node(ABC):
        """Represents a node in the command tree structure."""

        def __init__(self, name: str, description: Optional[str] = None, category: Optional[str] = None, callable_obj: Optional[Any] = None, children: Dict[str, 'Node'] = field(default_factory=dict), manifest: Optional[Manifest] = None):


        @abstractmethod
        def add_child(self, child: 'Node'):
            """Add a child node."""
            pass
        



@dataclass
class CommandNode:
    """Represents a node in the command tree structure."""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    callable_obj: Optional[Any] = None  # The actual function/method to call
    children: Dict[str, 'CommandNode'] = field(default_factory=dict)
    manifest: Optional[Manifest] = None
    
    def add_child(self, child: 'CommandNode'):
        """Add a child node."""
        self.children[child.name] = child
    
    def get_child(self, name: str) -> Optional['CommandNode']:
        """Get a child node by name."""
        return self.children.get(name)
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (has callable, no children)."""
        return self.callable_obj is not None and not self.children
    
    def is_group(self) -> bool:
        """Check if this is a group node (has children)."""
        return bool(self.children)

class CommandTree:
    """Builds and manages the command tree structure."""
    
    def __init__(self, manifest: Manifest):
        self.root_manifest = manifest
        self.visited_manifests = set()
    
    def build_tree(self) -> CommandNode:
        """Build the complete command tree from the root manifest."""
        self.visited_manifests.clear()
        return self._build_node(self.root_manifest)
    
    def _build_node(self, manifest: Manifest) -> CommandNode:
        """Build a single node in the command tree."""
        if manifest in self.visited_manifests:
            return CommandNode(name="cyclic", description="Cyclic reference detected")
        
        self.visited_manifests.add(manifest)
        
        # Create the root node
        node_name = manifest.location.shortName.split('.')[-1]  # Just the last part
        root_node = CommandNode(
            name=node_name,
            description=manifest.description,
            manifest=manifest
        )
        
        # Import the module
        module = importlib.import_module(manifest.location.module)
        
        # Determine what to inspect
        source_to_inspect = None
        is_module_manifest = manifest.location.classname is None
        is_package = is_module_manifest and manifest.location.isPackage
        
        if is_module_manifest:
            source_to_inspect = module
        else:
            # It's a class manifest
            header_class = getattr(module, manifest.location.classname, None)
            if header_class and issubclass(header_class, Header):
                impl_class = header_class._find_impl()
                source_to_inspect = impl_class if impl_class else header_class
        
        # Add Header classes as children
        if source_to_inspect and is_module_manifest:
            for name, obj in inspect.getmembers(source_to_inspect):
                if (inspect.isclass(obj) and issubclass(obj, Header) and 
                    hasattr(obj, '__manifest__') and obj.__manifest__ != manifest):
                    
                    # Check if this class is defined in this module (not just imported)
                    is_locally_defined = (
                        hasattr(obj, '__module__') and 
                        obj.__module__ == manifest.location.module
                    )
                    
                    # Include locally defined classes OR the Header base class itself
                    is_header_base_class = (name == "Header" and obj.__name__ == "Header")
                    
                    if is_locally_defined or is_header_base_class:
                        child_node = self._build_node(obj.__manifest__)
                        child_node.name = name  # Use the actual class name
                        child_node.category = "CLASS"
                        root_node.add_child(child_node)
        
        # Add exposed functions/methods
        if source_to_inspect:
            for name, obj in inspect.getmembers(source_to_inspect):
                if inspect.isfunction(obj) and getattr(obj, "_is_exposed", False):
                    func_node = CommandNode(
                        name=name,
                        description=obj.__doc__,
                        category="COMMANDS",
                        callable_obj=obj
                    )
                    root_node.add_child(func_node)
        
        # Add exposed methods from the current CLI instance (for any manifest)
        try:
            cli_instance = CLI(manifest=manifest)
            for name, method in inspect.getmembers(cli_instance, predicate=inspect.ismethod):
                if getattr(method, "_is_exposed", False):
                    func_node = CommandNode(
                        name=name,
                        description=method.__doc__,
                        category="COMMANDS",
                        callable_obj=method
                    )
                    root_node.add_child(func_node)
        except Exception:
            pass
        
        # Add submodules if this is a package
        if is_package:
            my_shortname = manifest.location.shortName
            spec = importlib.util.find_spec(my_shortname)
            if spec and spec.submodule_search_locations:
                for _, modname, ispkg in pkgutil.iter_modules(spec.submodule_search_locations):
                    if modname.startswith("__") and modname.endswith("__"):
                        continue
                    
                    sub_module_full_name = f"{my_shortname}.{modname}"
                    if sub_module_full_name == my_shortname:
                        continue
                    
                    try:
                        sub_module = importlib.import_module(sub_module_full_name)
                        if hasattr(sub_module, "__manifest__"):
                            # Check if the submodule has a header manifest (preferred)
                            header_manifest = None
                            
                            # Try pattern 1: module_h.py (flat structure)
                            try:
                                header_module_name = f"{sub_module_full_name}_h"
                                header_module = importlib.import_module(header_module_name)
                                if hasattr(header_module, "__manifest__"):
                                    header_manifest = header_module.__manifest__
                            except ImportError:
                                pass
                            
                            # Try pattern 2: module/__header__.py (nested structure) if flat didn't work
                            if not header_manifest and hasattr(sub_module, "__header__"):
                                try:
                                    header_module = importlib.import_module(f"{sub_module_full_name}.__header__")
                                    if hasattr(header_module, "__manifest__"):
                                        header_manifest = header_module.__manifest__
                                except ImportError:
                                    pass
                            
                            # Use header manifest if available, otherwise use module manifest
                            manifest_to_use = header_manifest if header_manifest else sub_module.__manifest__
                            
                            child_node = self._build_node(manifest_to_use)
                            child_node.category = "SUBMODULES"
                            root_node.add_child(child_node)
                    except Exception:
                        pass
        
        return root_node