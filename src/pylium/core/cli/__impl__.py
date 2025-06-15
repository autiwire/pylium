from .__header__ import CLI, Header
from pylium.manifest import Manifest
from pylium.core.header import expose

import importlib
import os
import fire
import functools
from typing import Any

def show_recursive_manifest(manifest: Manifest, indent_size = 2, level: int = 0):
    print(f"{' ' * indent_size * level} [{level+1}] {manifest.location.fqnShort}")
    for child in manifest.children:
        #print(f"{' ' * indent_size * indent} CHILD: {child.location.fqnShort}")
        if level < 5:
            show_recursive_manifest(child, indent_size, level + 1)


class CLIRenderer:
    """Renders a manifest hierarchy for python-fire consumption."""
    
    def __init__(self, manifest: Manifest):
        self._manifest = manifest
    
    def render(self) -> Any:
        """Render the manifest hierarchy as a python-fire (modified with category support) compatible object."""
        # Create a dynamic class to hold the commands
        class_attrs = {}
        
        # If the manifest is not CLI enabled, return None
        if not self._manifest.frontend & Manifest.Frontend.CLI:
            return None

        for child in self._manifest.children:
            if child.objectType not in self._manifest.objectType.possibleChildren():
                continue
            
            # Forbid children that are not allowed in the parent
            if not self._manifest.objectType.canContain(child.objectType):
                # TODO: Maybe we should raise an error here?
                #print(f"  SKIPPING CHILD: {child.location.fqnShort} ({child.objectType.name.upper()} not allowed in {self._manifest.objectType.name.upper()})")
                continue
                
            # Filter out children that are not exposed to CLI
            if not (child.frontend & Manifest.Frontend.CLI):
                #print(f"  SKIPPING CHILD: {child.location.fqnShort} (not exposed to CLI)")
                continue

            # Get the actual object from the manifest's location
            target_module = importlib.import_module(child.location.shortName)
            obj = None
            category = None

            if child.location.isPackage or child.location.isModule or child.location.isClass:
                # It's a package or module - recursively render it
                child_renderer = CLIRenderer(child)
                obj = child_renderer.render()                
                
                if child.location.isClass:
                    category = "CLASS"
                elif child.location.isModule:
                    category = "SUBMODULE"
                elif child.location.isPackage:
                    category = "SUBMODULE"

                if obj is not None:
                    obj.__fire_category__ = category

            elif child.location.isMethod:
                # It's a method - only include if it's not an implementation class
                my_class = getattr(target_module, child.location.classname)
                #print(f"  CLASS OBJ: {my_class} {type(my_class)}")

                my_func = getattr(my_class, child.location.funcname)
                #print(f"  OBJX: {my_func} {type(my_func)}")
                
                @functools.wraps(my_func)
                @fire.helptext.CommandCategory("METHOD")
                def method_wrapper(*args, **kwargs):
                    return my_func(*args, **kwargs)
               
                obj = method_wrapper

            elif child.location.isFunction:
                # It's a function - only include if it's not an implementation class
                my_func = getattr(target_module, child.location.funcname)
                @functools.wraps(my_func)
                @fire.helptext.CommandCategory("FUNCTION")
                def function_wrapper(*args, **kwargs):
                    return my_func(*args, **kwargs)
                
                obj = function_wrapper

            if obj is not None:               
                name = child.location.localName
                if name is not None:
                    class_attrs[name] = obj
                else:
                    print(f"  SKIPPING CHILD: {child.location.fqnShort} (no local name)")
                    continue
                
       
        # Create and return a dynamic class instance
        DynamicCLI = type('DynamicCLI', (), class_attrs)
        cli_instance = DynamicCLI()
        cli_instance.__doc__ = self._manifest.description
        cli_instance.__name__ = self._manifest.location.localName
        return cli_instance

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
    
    def start(self, **kwargs):
        """
        Builds the CLI from exposed methods and sub-modules, then runs it.
        """
        # Render the tree for python-fire
        renderer = CLIRenderer(self._target_manifest)
        cli_target = renderer.render()

        if "PAGER" not in os.environ:
            os.environ["PAGER"] = "cat"
        
        #print(f"  CLI TARGET: {cli_target} {type(cli_target)} name: {self._target_manifest.location.fqnShort}")
        fire.Fire(cli_target, name=self._target_manifest.location.fqnShort)

    def stop(self):
        """
        Stops the CLI.
        """
        pass

    def is_running(self):
        """
        Checks if the CLI is currently running.
        """
        return False

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