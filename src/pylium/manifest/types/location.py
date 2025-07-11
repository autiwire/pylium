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

# External imports
from pydantic import Field, computed_field

class ManifestLocation(ManifestValue):
    """A location in the manifest system, identifying a module, class, or function."""
    module: str = Field(..., description="The module name")
    classname: Optional[str] = Field(default=None, description="Optional class name (typically __qualname__ for classes)")
    funcname: Optional[str] = Field(default=None, description="Optional function name (typically __qualname__ for functions)")

    def _get_short_name(self, module_name: str) -> str:
        """Returns the module name with implementation suffixes removed."""
        remove_strs = [".__header__", ".__impl__", "_h", "_impl"]
        for remove_str in remove_strs:
            if module_name.endswith(remove_str):
                return module_name[:-len(remove_str)]
        return module_name

    @computed_field
    @property
    def file(self) -> str:
        """The file location from the module name."""
        spec = importlib.util.find_spec(self.module)
        if spec is None or spec.origin is None:
            raise ImportError(f"Could not find module {self.module}")
        return str(Path(spec.origin).resolve())

    @computed_field
    @property
    def shortName(self) -> str:
        """Returns the module name with implementation suffixes removed."""
        return self._get_short_name(self.module)

    @computed_field
    @property
    def fqn(self) -> str:
        """Fully qualified name."""
        if self.funcname and self.classname:
            return f"{self.module}.{self.classname}.{self.funcname}"
        elif self.classname:
            return f"{self.module}.{self.classname}"
        elif self.funcname:
            return f"{self.module}.{self.funcname}"
        else:
            return self.module

    @computed_field
    @property
    def fqnShort(self) -> str:
        """Short fully qualified name."""
        short_name = self.shortName
        if self.funcname and self.classname:
            return f"{short_name}.{self.classname}.{self.funcname}"
        elif self.classname:
            return f"{short_name}.{self.classname}"
        elif self.funcname:
            return f"{short_name}.{self.funcname}"
        else:
            return short_name

    @computed_field
    @property
    def localName(self) -> Optional[str]:
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

    def __str__(self) -> str:
        return f"{self.fqn}"
    
    def __repr__(self) -> str:
        return f"{self.fqn} @ {self.file}"

    @computed_field
    @property
    def isPackage(self) -> bool:
        """Checks if the location points to a package (and not a single .py file)"""
        spec = importlib.util.find_spec(self.shortName)
        return self.isModule and spec is not None and spec.submodule_search_locations is not None and len(spec.submodule_search_locations) > 0
    
    @computed_field
    @property
    def isModule(self) -> bool:
        """Checks if the location points to a module."""
        return self.classname is None and self.funcname is None

    @computed_field
    @property
    def isClass(self) -> bool:
        """Checks if the location points to a class."""
        return self.classname is not None and self.funcname is None
    
    @computed_field
    @property
    def isFunction(self) -> bool:
        """Checks if the location points to a function."""
        return self.funcname is not None

    @computed_field
    @property
    def isMethod(self) -> bool:
        """Checks if the location points to a method."""
        return self.funcname is not None and self.classname is not None
    
    @computed_field
    @property
    def isClassMethod(self) -> bool:
        """Checks if the location points to a @classmethod."""
        if not (self.classname and self.funcname):
            return False
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.classname, None)
        if cls is None:
            return False
        attr = inspect.getattr_static(cls, self.funcname, None)
        return isinstance(attr, classmethod)

    @computed_field
    @property
    def isStaticMethod(self) -> bool:
        """Checks if the location points to a @staticmethod."""
        if not (self.classname and self.funcname):
            return False
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.classname, None)
        if cls is None:
            return False
        attr = inspect.getattr_static(cls, self.funcname, None)
        return isinstance(attr, staticmethod)