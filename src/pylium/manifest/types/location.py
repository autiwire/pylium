"""
Location type for the manifest.
"""

# Pylium imports
from .value import ManifestValue

# Built-in imports
from typing import Optional
import importlib
import inspect
from pathlib import Path


class ManifestLocation(ManifestValue):
    def __init__(self, module: str, classname: Optional[str] = None, funcname: Optional[str] = None):
        """
        Create a manifest location.
        
        Args:
            module: The module name:
                   - If modules: use __name__
                   - If classes: use __module__
            
            classname: Optional class name (typically __qualname__ for classes)

            funcname: Optional function name (typically __qualname__ for functions)

        """
        self.module = module
        self.classname = classname
        self.funcname = funcname

        # Get the file location from the module name
        spec = importlib.util.find_spec(self.module)
        if spec is None or spec.origin is None:
            raise ImportError(f"Could not find module {self.module}")
            
        self.file = str(Path(spec.origin).resolve())        
        if self.funcname and self.classname:
            self.fqn = f"{self.module}.{self.classname}.{self.funcname}"
            self.fqnShort = f"{self.shortName}.{self.classname}.{self.funcname}"
        elif self.classname:
            self.fqn = f"{self.module}.{self.classname}"
            self.fqnShort = f"{self.shortName}.{self.classname}"
        elif self.funcname:
            self.fqn = f"{self.module}.{self.funcname}"
            self.fqnShort = f"{self.shortName}.{self.funcname}"
        else:
            self.fqn = self.module
            self.fqnShort = self.shortName

    @property
    def shortName(self) -> str:
        """Returns the module name with implementation suffixes removed."""
        remove_strs = [".__header__", ".__impl__", "_h", "_impl"]
        module_name = self.module
        for remove_str in remove_strs:
            if module_name.endswith(remove_str):
                return module_name[:-len(remove_str)]
        return module_name

    @property
    def localName(self) -> str:
        """Returns the local name of the location."""
        if self.isPackage:
            return self.shortName.split(".")[-1]
        elif self.isModule:
            return self.shortName.split(".")[-1]
        elif self.isClass:
            return self.classname
        elif self.isMethod:
            return self.funcname
        elif self.isFunction:
            return self.funcname
        else:
            return None

    def __str__(self):
        return f"{self.fqn}"
    
    def __repr__(self):
        return f"{self.fqn} @ {self.file}"

    @property
    def isPackage(self) -> bool:
        """
        Checks if the location points to a package (and not a single .py file)
        """
        spec = importlib.util.find_spec(self.shortName)
        #print(f"DEBUG: spec: {spec}") # DEBUG
        #print(f"DEBUG: spec.submodule_search_locations: {spec.submodule_search_locations}") # DEBUG
        return self.isModule and spec is not None and spec.submodule_search_locations is not None and len(spec.submodule_search_locations) > 0
    
    @property
    def isModule(self) -> bool:
        """
        Checks if the location points to a module.
        """
        return self.classname is None and self.funcname is None

    @property
    def isClass(self) -> bool:
        """
        Checks if the location points to a class.
        """
        return self.classname is not None and self.funcname is None
    
    @property
    def isFunction(self) -> bool:
        """
        Checks if the location points to a function.
        """
        return self.funcname is not None

    @property
    def isMethod(self) -> bool:
        """
        Checks if the location points to a method.
        """
        return self.funcname is not None and self.classname is not None
    
    @property
    def isClassMethod(self) -> bool:
        """
        Checks if the location points to a @classmethod.
        """
        if not (self.classname and self.funcname):
            return False
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.classname, None)
        if cls is None:
            return False
        attr = inspect.getattr_static(cls, self.funcname, None)
        return isinstance(attr, classmethod)


    @property
    def isStaticMethod(self) -> bool:
        """
        Checks if the location points to a @staticmethod.
        """
        if not (self.classname and self.funcname):
            return False
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.classname, None)
        if cls is None:
            return False
        attr = inspect.getattr_static(cls, self.funcname, None)
        return isinstance(attr, staticmethod)