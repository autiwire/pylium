from .__header__ import CLI, Header
from pylium.manifest import Manifest

import importlib
import os
import fire
import functools
from typing import Any
import inspect


class CLIRenderer:
    """Renders a manifest hierarchy for python-fire consumption."""
    
    def __init__(self, manifest: Manifest):
        self._manifest = manifest
    
    @staticmethod
    def make_function_wrapper(func):
        """Creates a properly bound function wrapper that preserves the original function."""
        @functools.wraps(func)
        @fire.helptext.CommandCategory("FUNCTION")
        def function_wrapper(self, *args, **kwargs):
            # If it's an instance method, we need to handle self
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            if params and params[0].name == 'self':
                # It's an instance method, try to get default instance
                try:
                    if hasattr(func.__self__.__class__, 'default'):
                        instance = func.__self__.__class__.default
                    else:
                        instance = func.__self__.__class__()
                    return func(instance, *args, **kwargs)
                except Exception as e:
                    print(f"Error creating instance: {e}")
                    return func(*args, **kwargs)
            else:
                # Regular function, just call it
                return func(*args, **kwargs)
        
        # Create a signature without duplicating self
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if params and params[0].name == 'self':
            # Already has self, use as is
            function_wrapper.__signature__ = sig
        else:
            # Add self parameter
            new_params = [inspect.Parameter('self', inspect.Parameter.POSITIONAL_OR_KEYWORD)] + params
            function_wrapper.__signature__ = inspect.Signature(new_params)
        return function_wrapper
    
    def render(self) -> Any:
        """Render the manifest hierarchy as a python-fire (modified with category support) compatible object."""
        # Create a dynamic class to hold the commands
        class_attrs = {}
        
        # If the manifest is not CLI enabled, return None
        if not self._manifest.frontend & Manifest.Frontend.CLI:
            return None

        for child in self._manifest.children:
            #print(f"  CHILD: {child.location.fqnShort} {child.objectType.name.upper()} {self._manifest.objectType.name.upper()}")
            if child.objectType not in self._manifest.objectType.possibleChildren():
                print(f"  SKIPPING CHILD: {child.location.fqnShort} ({child.objectType.name.upper()} not allowed in {self._manifest.objectType.name.upper()})")
                continue
            
            #print(f"  ALLOWED CHILD: {child.location.fqnShort} {child.objectType.name.upper()} {self._manifest.objectType.name.upper()}")

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
                # It's a method - handle different method types
                my_class = getattr(target_module, child.location.classname)
                my_func = getattr(my_class, child.location.funcname)
                
                #print(f"  DEBUG: {child.location.fqnShort}")
                #print(f"    isClassMethod: {child.location.isClassMethod}")
                #print(f"    isStaticMethod: {child.location.isStaticMethod}")
                #print(f"    isMethod: {child.location.isMethod}")
                
                # TODO: FIX -> CLOSURE FACTORY??
                @functools.wraps(my_func)
                @fire.helptext.CommandCategory("METHOD")
                def method_wrapper(*args, **kwargs):
                    if child.location.isClassMethod:
                        # Class method - call with class
                        return my_func(my_class, *args, **kwargs)
                    elif child.location.isStaticMethod:
                        # Static method - call directly
                        return my_func(*args, **kwargs)
                    else:
                        # Instance method - try to get default instance, otherwise create new
                        try:
                            # Try to get default instance (e.g., Crowbar.default)
                            if hasattr(my_class, 'default'):
                                instance = my_class.default
                            else:
                                # Create new instance
                                instance = my_class()
                            return my_func(instance, *args, **kwargs)
                        except Exception as e:
                            print(f"Error creating instance for {child.location.fqnShort}: {e}")
                            # Fallback: try direct call (Fire might handle it)
                            return my_func(*args, **kwargs)
                obj = method_wrapper


            elif child.location.isFunction:
                # It's a function - create a properly bound wrapper using the factory
                my_func = getattr(target_module, child.location.funcname)
                obj = self.make_function_wrapper(my_func)

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

#    @expose
#    def info(self):
#        """
#        Displays detailed manifest information for the current component.
#        """
#        return self._target_manifest.doc
