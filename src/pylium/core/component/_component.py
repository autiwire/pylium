from ._component_meta import ComponentMetaclass
from ._component_base import ComponentBase

from typing import Type, ClassVar, Optional

import logging
import importlib
import inspect

logger = logging.getLogger(__name__)

class Component(ComponentBase, metaclass=ComponentMetaclass):

    Base = ComponentBase
    Metaclass = ComponentMetaclass

    @classmethod
    def _find_impl(cls) -> Type["Component"]:
        my_module = cls.__module__
        # TODO: Refine this list based on actual module structure needs
        impl_modules_names = [f"{my_module}", f"{my_module}_impl", f"_impl"] # Added module prefix for relative _impl

        impl_cls = None
        for module_name in impl_modules_names:
            try:
                imported_module = importlib.import_module(module_name)
                logger.debug(f"  Successfully imported potential impl module: {module_name}")

                # Inspect members of the imported module
                for name, obj in inspect.getmembers(imported_module):
                    logger.debug(f"    Checking member: {name} ({type(obj)})")
                    # Check if obj is a class, is not the header class itself,
                    # inherits cls directly, and name ends with "Impl" (convention)
                    if (inspect.isclass(obj) and 
                            obj is not cls and
                            Component._has_direct_base_subclass(obj, cls)):
                        logger.debug(f"    Found matching implementation class by convention: {obj.__name__}")
                        impl_cls = obj
                        break # Found the class in this module, exit inner loop
            
            except ImportError:
                logger.debug(f"  Could not import potential impl module: {module_name}")
                continue # Skip if module doesn't exist
            except Exception as e: # Catch other potential errors during import/inspection
                 logger.warning(f"  Error inspecting module {module_name}: {e}")
                 continue

            if impl_cls:
                break # Found the class, exit outer loop

        if not impl_cls:
             logger.debug(f"  No implementation class found after searching: {impl_modules_names}")

        return impl_cls

    def __init__(self, *args, **kwargs):
        # This __init__ will run on the *implementation* instance if discovered,
        # or on the header instance if _no_impl is True.
        logger.debug(f"Component __init__: {self.__class__.__name__} called with args: {args}, kwargs: {kwargs}")
        try:
            logger.debug(f"  self.__class__ is not object, calling super().__init__(*args, **kwargs)")
            super().__init__(*args, **kwargs)
        except TypeError as e:
            logger.warning(f"Potential issue during super().__init__ in {self.__class__.__name__}: {e}. Args: {args}, Kwargs: {kwargs}")

    def __new__(cls, *args, **kwargs):
        logger.debug(f"Component __new__: {cls.__name__} called with args: {args}, kwargs: {kwargs}")

        # Case 1 & 2: If this IS the impl class OR we are told not to load one,
        # create the instance directly using the standard object creation mechanism.
        if cls._is_impl or cls._no_impl:
            logger.debug(f"  Creating instance of {cls.__name__} directly (is_impl={cls._is_impl}, no_impl={cls._no_impl}).")
            instance = super().__new__(cls)
            logger.debug(f"  Component __new__ (direct) returning instance: {instance}")
            return instance
        
        # Case 3: This is a "Header" class needing an implementation.
        logger.debug(f"  {cls.__name__} is a Header, finding implementation...")
        impl_cls = cls._find_impl()

        if impl_cls:
            # Sanity check (optional but good)
            if not getattr(impl_cls, '_is_impl', False):
                 raise RuntimeError(f"Discovered class {impl_cls.__name__} for {cls.__name__} is not marked as an implementation (_is_impl is not True)")
            
            logger.debug(f"  Found implementation {impl_cls.__name__}, instantiating it instead.")
            # Instantiate the implementation class. This call will trigger:
            # 1. impl_cls.__new__(impl_cls, *args, **kwargs)
            # 2. Which will enter Case 1 above (since impl_cls._is_impl is True)
            # 3. Which calls super().__new__(impl_cls) correctly.
            # 4. Python then calls __init__ on the returned instance with *args, **kwargs.
            instance = impl_cls(*args, **kwargs)
            logger.debug(f"  Component __new__ (via impl) returning instance: {instance} of type {type(instance)}")
            return instance
        else:
            # Case 4: Header class, but no implementation found.
            raise RuntimeError(f"No implementation class found for Header {cls.__name__}")

    def __init_subclass__(cls, **kwargs):
        logger.debug(f"Component __init_subclass__: {cls.__name__}")
        super().__init_subclass__(**kwargs)
        

    # Add other common Component methods/attributes here if needed
    pass

    