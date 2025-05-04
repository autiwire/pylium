# Pylium Component Base

from ._module import ComponentModule

import threading
from typing import ClassVar

import logging
import importlib
logger = logging.getLogger(__name__)

class ComponentBase:
    """
    Base class for Pylium core components
    """

    # Per-class implementation setting - set this to True in impl classes
    _is_impl: ClassVar[bool] = False # False by default -> header class, set to True in impl classes
    _no_impl: ClassVar[bool] = False # False by default -> disables loading of impl classes

    _cls_logger: ClassVar[logging.LoggerAdapter] = None
    _cls_logger_mutex: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def pylium(cls) -> 'ComponentModule':
        """
        Get the ComponentModule instance ('pylium') for the module 
        where this class is defined.
        """
        module_name = cls.__module__
        try:
            module_obj = importlib.import_module(module_name)
            
            # Use getattr to safely access 'pylium' attribute
            module_pylium_instance = getattr(module_obj, 'pylium', None) 

            # Check if it exists and is the correct type (assuming ComponentModule is available)
            # Ensure ComponentModule is imported in this file or use isinstance check carefully
            if module_pylium_instance is None or not isinstance(module_pylium_instance, ComponentModule):
                 logger.error(f"Module {module_name} loaded but has no valid 'pylium' attribute of type ComponentModule.")
                 raise ValueError(f"Module {module_name} does not contain a valid 'pylium' ComponentModule instance.")
            
            logger.debug(f"Found pylium instance for {module_name}")
            return module_pylium_instance # Return the found instance

        except ImportError:
            logger.error(f"Could not import module {module_name} to retrieve its pylium instance.")
            raise ValueError(f"Module {module_name} could not be imported.")
        except Exception as e:
             logger.error(f"Error retrieving pylium instance from {module_name}: {e}", exc_info=True)
             raise # Re-raise unexpected errors

    #@classmethod
    #def logger(cls) -> logging.LoggerAdapter:
    #    """
    #    Get a logger for the component (Class Logger Adapter -> Module Logger)
    #    """
        
    #    if cls._cls_logger is None:
    #        with cls._cls_logger_mutex:
    #        if cls._cls_logger is None:
    #            # Find "pylium" in module of cls
    #            module = cls.__module__
    #            if "pylium" not in module:
    #                raise ValueError(f"Module {module} is not a Pylium module")
    #            cls._cls_logger = logging.LoggerAdapter(module.pylium.logger, {"module": module}) 
        
    #    return cls._cls_logger

    @staticmethod
    def _has_direct_base_subclass(A: type, B: type) -> bool:
        """
        Returns True if A has B (or a subclass of B) as a direct base class.
        Handles potential TypeErrors if A.__bases__ is not available.
        """
        try:
             # Check direct bases only
             return any(base is B or (isinstance(base, type) and issubclass(base, B)) for base in A.__bases__)
        except AttributeError:
             logger.warning(f"Could not access __bases__ for type {A} during check.")
             return False

    # Catches __init__ args and kwargs before passing them to the superclass, which is object
    def __init__(self, *args, **kwargs):
        logger.debug(f"ComponentBase __init__: {self.__class__.__name__} called with args: {args}, kwargs: {kwargs}")
        super().__init__()

