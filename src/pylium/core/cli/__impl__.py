from .__header__ import CLI, Header
from pylium.manifest import Manifest
from pylium.core.header import expose

import importlib
import os
import fire
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
        
        print(f"[{self._manifest.objectType.name.upper()}] MANIFEST: {self._manifest.location.fqnShort}")
        print(f"  possibleChildren: {self._manifest.objectType.possibleChildren()}")

        #show_recursive_manifest(self._manifest, indent_size=1)
        #import sys
        #sys.exit(0)

        # If the manifest is not CLI enabled, return None
        if not self._manifest.frontend & Manifest.Frontend.CLI:
            return None

        #print(f"  OBJTYPE: {self._manifest.objectType}")
        #print(f"  isPackage: {self._manifest.location.isPackage}")
        #print(f"  isModule: {self._manifest.location.isModule}")
        #print(f"  isClass: {self._manifest.location.isClass}")
        #print(f"  isMethod: {self._manifest.location.isMethod}")
        #print(f"  isFunction: {self._manifest.location.isFunction}")


        for child in self._manifest.children:
            if child.objectType not in self._manifest.objectType.possibleChildren():
                print(f"  SKIPPING CHILD: {child.location.fqnShort} ({child.objectType.name.upper()} not allowed in {self._manifest.objectType.name.upper()})")
                print(f"  isPackage: {child.location.isPackage}")
                print(f"  isModule: {child.location.isModule}")
                print(f"  isClass: {child.location.isClass}")
                print(f"  isMethod: {child.location.isMethod}")
                print(f"  isFunction: {child.location.isFunction}")
                continue
            
            print(f"  CHILD: {child.location.fqnShort}")

            # Forbid children that are not allowed in the parent
            if not self._manifest.objectType.canContain(child.objectType):
                # TODO: Maybe we should raise an error here?
                print(f"  SKIPPING CHILD: {child.location.fqnShort} ({child.objectType.name.upper()} not allowed in {self._manifest.objectType.name.upper()})")
                continue
                
            # Filter out children that are not exposed to CLI
            if not (child.frontend & Manifest.Frontend.CLI):
                print(f"  SKIPPING CHILD: {child.location.fqnShort} (not exposed to CLI)")
                continue

            # Get the actual object from the manifest's location
            target_module = importlib.import_module(child.location.shortName)
            obj = None

            if child.location.isPackage or child.location.isModule or child.location.isClass:
                # It's a package or module - recursively render it
                child_renderer = CLIRenderer(child)
                obj = child_renderer.render()
            elif child.location.isMethod:
                # It's a method - only include if it's not an implementation class
                class_obj = getattr(target_module, child.location.classname)
                obj = getattr(class_obj, child.location.funcname)
            elif child.location.isFunction:
                # It's a function - only include if it's not an implementation class
                obj = getattr(target_module, child.location.funcname)

            if obj is not None:
                name = child.location.localName
                if name is not None:
                    class_attrs[name] = obj
                else:
                    print(f"  SKIPPING CHILD: {child.location.fqnShort} (no local name)")
                    continue
                

        #print("--------------------------------")
        #print(f"MANIFEST: {self.manifest.location.shortName}")
        #for child in self.manifest.children:            
            #print(f"  CHILD: {child.location.fqnShort}")
        #print("")

        #for child in self._manifest.children:
        #    print(f"  CHILD: {child.location.fqnShort}")

        # Process all children of the manifest
        for child in self._manifest.children:
            continue
            #print(f"  CHILD: {child.location.fqnShort}")
            
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
                    # It's a class - only include if it's not an implementation class
                    if hasattr(class_obj, '__manifest__'):
                        if class_obj.__manifest__.frontend & Manifest.Frontend.CLI:
                            child_renderer = CLIRenderer(class_obj.__manifest__)
                            obj = child_renderer.render()
                            
                    #if not hasattr(class_obj, '__class_type__') or class_obj.__class_type__ != Header.ClassType.Impl:
                        #obj = class_obj
                        #pass
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
        
        fire.Fire(cli_target, name=self._target_manifest.location.shortName)

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