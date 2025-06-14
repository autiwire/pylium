from .__header__ import CLI, Header
from pylium.manifest import Manifest
from pylium.core.header import expose

import importlib
import os
import fire
from typing import Any


class CLIRenderer:
    """Renders a manifest hierarchy for python-fire consumption."""
    
    def __init__(self, manifest: Manifest):
        self.manifest = manifest
    
    def render(self) -> Any:
        """Render the manifest hierarchy as a python-fire compatible object."""
        # Create a dynamic class to hold the commands
        class_attrs = {}
        
        #print("--------------------------------")
        #print(f"MANIFEST: {self.manifest.location.shortName}")
        #for child in self.manifest.children:            
            #print(f"  CHILD: {child.location.fqnShort}")
        #print("")

        # Process all children of the manifest
        for child in self.manifest.children:
            #print(f"CHILD: {child.location.shortName} vs {self.manifest.location.module}")
            
            # Only include manifests that are exposed to CLI
            if not (child.frontend & Manifest.Frontend.CLI):
                continue
                
            # Get the actual object from the manifest's location
            target_module = importlib.import_module(child.location.shortName)
            obj = None
            
            if child.location.classname:
                # It's a class or method
                class_obj = getattr(target_module, child.location.classname)
                if child.location.funcname:
                    # It's a method
                    obj = getattr(class_obj, child.location.funcname)
                else:
                    # It's a class
                    obj = class_obj
            else:
                # It's a module or function
                if child.location.funcname:
                    # It's a function
                    obj = getattr(target_module, child.location.funcname)
                else:
                    # It's a module - recursively render it
                    child_renderer = CLIRenderer(child)
                    obj = child_renderer.render()
            
            if obj is not None:
                # Set the category based on manifest type
                category = None
                if child.location.classname and not child.location.funcname:
                    category = "CLASS"
                elif child.location.funcname:
                    category = "COMMANDS"
                elif not child.location.classname and not child.location.funcname:
                    category = "SUBMODULES"
                
                try:
                    obj.__fire_category__ = category
                except (AttributeError, TypeError):
                    # If we can't set it directly, create a wrapper
                    class CallableWrapper:
                        def __init__(self, func, category):
                            self._func = func
                            self.__fire_category__ = category
                        
                        def __call__(self, *args, **kwargs):
                            return self._func(*args, **kwargs)
                        
                        def __getattr__(self, name):
                            return getattr(self._func, name)
                    
                    obj = CallableWrapper(obj, category)
                
                # Use the proper name from the location
                if child.location.classname:
                    name = child.location.classname
                else:
                    name = child.location.shortName.split('.')[-1]
                class_attrs[name] = obj
        
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
        # Render the tree for python-fire
        renderer = CLIRenderer(self._target_manifest)
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