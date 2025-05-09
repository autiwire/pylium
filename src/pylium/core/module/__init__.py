from typing import List, ClassVar, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod
import os
import sys

import logging
logger = logging.getLogger(__name__)

class _ModuleType(Enum):
    NONE = "none"
    MODULE = "module"
    PACKAGE = "package"
    PROJECT = "project"

    def __str__(self):
        return self.value

class _ModuleBase(ABC):
    """
    An abstract base class for all pylium modules.
    """
   
    Type = _ModuleType

    name: ClassVar[str] = ""
    fqn: ClassVar[str] = ""
    file: ClassVar[Optional[str]] = None
    type: ClassVar[Type] = Type.NONE
    version: ClassVar[str] = "0.0.0"
    description: ClassVar[str] = ""
    dependencies: ClassVar[List[str]] = []
    authors: ClassVar[List[str]] = []

    @classmethod
    def _init_var(cls, varname: str, value: Any):
        if not varname in cls.__dict__:
            setattr(cls, varname, value)

    def __init_subclass__(cls, **kwargs) -> None:
        logger.debug(f"Module __init_subclass__ for: {cls.__name__}")
        super().__init_subclass__(**kwargs)

        # --- Phase 1: Determine and establish basic module identity (name, file) ---
        # These are foundational and might be used by subclasses or to derive other attributes.
        
        # Get module name from where the class 'cls' is defined
        detected_module_dot_name = cls.__module__
        cls._init_var("name", detected_module_dot_name)

        # Get module file path
        actual_module_obj = sys.modules.get(detected_module_dot_name)
        detected_file_path = None
        if actual_module_obj and hasattr(actual_module_obj, '__file__') and actual_module_obj.__file__ is not None:
            detected_file_path = actual_module_obj.__file__
        cls._init_var("file", detected_file_path)

        # --- Phase 2: Determine and establish derived attributes (fqn, type, description) ---
        # These use the now-established cls.name and cls.file (which could be from subclass or defaulted).

        # Determine fqn (Fully Qualified Name)
        # Uses cls.name and cls.file which are now set (either by subclass or _init_var above)
        current_name = cls.name # Should be module path like 'my.package.module'
        current_file = cls.file
        default_fqn = current_name
        if current_file and os.path.basename(current_file) == "__init__.py":
            default_fqn = f"{current_name}.__init__"
        cls._init_var("fqn", default_fqn)

        # Determine type (MODULE or PACKAGE)
        default_type = _ModuleBase.Type.MODULE # Default to MODULE
        if current_file and os.path.basename(current_file) == "__init__.py":
            default_type = _ModuleBase.Type.PACKAGE
        cls._init_var("type", default_type)
        
        # Set description from docstring if not overridden
        default_description = cls.__doc__ if cls.__doc__ is not None else ""
        cls._init_var("description", default_description.strip())

    def __init__(self, *args, **kwargs):
        """
        Initialize the Module.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name} (Type: {self.type}, FQN: {self.fqn})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.type}', fqn='{self.fqn}', file='{self.file}')"

class Module(_ModuleBase):
    """
    A module represented by a single Python (.py) file.
    """
    type: ClassVar[_ModuleBase.Type] = _ModuleBase.Type.MODULE
    version: ClassVar[str] = "0.0.1"

__all__ = ["Module"]