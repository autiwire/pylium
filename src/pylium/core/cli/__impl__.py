from .__header__ import CLI, Header
from pylium.manifest import Manifest
from pylium.core.header import expose

import pkgutil
import importlib
import inspect
import os
import fire
import sys
from typing import ClassVar, Dict, Any, Optional, List, Union
from dataclasses import dataclass, field

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

class CLIRenderer:
    """Renders a command tree for python-fire consumption."""
    
    def __init__(self, tree: CommandNode):
        self.tree = tree
    
    def render(self) -> Any:
        """Render the command tree as a python-fire compatible object."""
        if self.tree.is_leaf():
            return self.tree.callable_obj
        
        # Create a dynamic class to hold the commands
        class_attrs = {}
        
        # Group children by category
        for child in self.tree.children.values():
            if child.is_leaf():
                # It's a callable command
                obj = child.callable_obj
                try:
                    # Try to set category directly on the object
                    obj.__fire_category__ = child.category
                except (AttributeError, TypeError):
                    # If we can't set it directly (e.g., method objects), create a wrapper
                    class CallableWrapper:
                        def __init__(self, func, category):
                            self._func = func
                            self.__fire_category__ = category
                        
                        def __call__(self, *args, **kwargs):
                            return self._func(*args, **kwargs)
                        
                        def __getattr__(self, name):
                            return getattr(self._func, name)
                    
                    obj = CallableWrapper(obj, child.category)
                
                class_attrs[child.name] = obj
            else:
                # It's a group - recursively render it
                child_renderer = CLIRenderer(child)
                instance = child_renderer.render()
                try:
                    instance.__fire_category__ = child.category
                except (AttributeError, TypeError):
                    # If instance doesn't support setting attributes, that's okay
                    pass
                class_attrs[child.name] = instance
        
        # Create and return a dynamic class instance
        DynamicCLI = type('DynamicCLI', (), class_attrs)
        return DynamicCLI()

class CategorizedCommands(dict):
    """A dictionary wrapper that carries a fire category."""
    def __init__(self, commands, category=None):
        super().__init__(commands)
        if category:
            self.__fire_category__ = category

class CLIImpl(CLI):
    """
    Implementation of the recursive, lazy-loading CLI builder.
    """
    __class_type__ = Header.ClassType.Impl

    def __init__(self, manifest: Manifest):
        self._target_manifest = manifest
        # No super() call needed as the Header's init is abstract
        # Eager loading removed, we will use explicit methods.

    def __str__(self):
        # This is shown by python-fire as the main help text if no commands are exposed.
        return self._target_manifest.description or ""
    
    def start(self):
        """
        Builds the CLI from exposed methods and sub-modules, then runs it.
        """
        # Build the command tree
        tree_builder = CommandTree(self._target_manifest)
        command_tree = tree_builder.build_tree()
        
        # Render the tree for python-fire
        renderer = CLIRenderer(command_tree)
        cli_target = renderer.render()

        if "PAGER" not in os.environ:
            os.environ["PAGER"] = "cat"
        
        fire.Fire(cli_target, name=self._target_manifest.location.shortName)

    # --- Exposed Commands ---

    @expose
    def info(self):
        """
        Displays detailed manifest information for the current component.
        """
        return self._target_manifest.doc

# We can now add public methods here that will be exposed by fire.
# For example, a method to list available sub-modules:
#
#    def list(self):
#        '''Lists available commands.'''
#        # ... discovery logic ... 