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

    def __str__(self):
        return self.value

class _ModuleBase(ABC):
    """
    A hidden base class for all pylium modules.
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
        cls._init_var("description", default_description)

    def __init__(self, *args, **kwargs):
        """
        Initialize the Module.
        """
        pass

    def __str__(self):
        return f"Module: {self.name}"
    
    def __repr__(self):
        return f"Module: {self.name}"

class Module(_ModuleBase):
    """
    A module is a single python file. 

    This class shall be used to describe the module and its dependencies.    
    """
 

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)



# Initialize attributes for the Module class itself
#Module.file = __file__  # The __file__ of this pylium.core.module.__init__ module
#Module.name = __name__  # The __name__ of this module (e.g., "pylium.core.module")
#if Module.file and os.path.basename(Module.file) == "__init__.py":
#    Module.fqn = f"{__name__}.__init__"
#else:
#    Module.fqn = __name__
#logger.debug(f"Module class initialized: name={Module.name}, fqn={Module.fqn}, file={Module.file}")
    
__all__ = ["Module"]




# def __init__(self, 
#            settings_class: Optional[Type[ComponentModuleConfig]] = None,
#            logger: Optional[logging.Logger] = None,
