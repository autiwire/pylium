from .__header__ import Header

from typing import Type
from pathlib import Path
import inspect
import importlib

import logging
logger = logging.getLogger(__name__)


class HeaderImpl(Header):
    """
    Implementation class for the Header class.
    """
    __class_type__ = Header.ClassType.Impl


    # Find the implementation class for this header
    @classmethod
    def _find_impl(cls) -> Type["Header"]:
        """
        Find the implementation class for this header.
        """

        print(f"  Finding implementation for {cls.__name__} @ {cls.__module__}")

        # Manual settings always take precedence
        if cls.__implementation__:
            logger.debug(f"  {cls.__name__} has manual implementation setting: {cls.__implementation__}")
            return cls.__implementation__

        # we need to determine whether we need to find the implementation
        if cls.__class_type__ == Header.ClassType.Bundle:
            logger.debug(f"  {cls.__name__} is a Bundle, we are already an implementation...")
            return cls
        
        elif cls.__class_type__ == Header.ClassType.Impl:
            logger.debug(f"  {cls.__name__} is an Impl, we are already an implementation...")
            return cls
        
        
        elif cls.__class_type__ == Header.ClassType.Header:
            logger.debug(f"  {cls.__name__} is a Header, finding implementation...")

            # Step 1: Determine the target implementation module name
            target_impl_module_fqn = None
            try:
                header_module_path = Path(inspect.getfile(cls))
                header_module_name_stem = header_module_path.stem # File name without extension
                header_package_dot_path = '.'.join(cls.__module__.split('.')[:-1])

                if header_module_name_stem == "__header__":
                    target_impl_module_stem = "__impl__"
                elif header_module_name_stem.endswith("_h"):
                    target_impl_module_stem = header_module_name_stem[:-2] + "_impl"
                else:
                    # Fallback: attempt to find an Impl class in the same module or a conventionally named one.
                    # For now, if no specific header naming convention (_h or __header__) is met,
                    # we'll log and this will likely lead to not finding an explicit impl module.
                    # The class search logic later might find an Impl class in the same module.
                    logger.warning(
                        f"  Header class {cls.__module__}.{cls.__name__} module filename '{header_module_path.name}' "
                        f"does not follow __header__.py or <name>_h.py convention. "
                        f"Implementation must be in the same module or explicitly defined via __implementation__."
                    )
                    # In this case, target_impl_module_fqn remains None, or we could default to cls.__module__
                    # to search for an Impl class within the same module file.
                    # For now, let's assume the _impl module is distinct if conventions are used.
                    # If no convention, the later class search might still find an Impl subclass in the same module.
                    target_impl_module_stem = None # Indicates no separate _impl module by convention

                if target_impl_module_stem:
                    if header_package_dot_path:
                        target_impl_module_fqn = f"{header_package_dot_path}.{target_impl_module_stem}"
                    else: # Should not happen for typical project structures
                        target_impl_module_fqn = target_impl_module_stem
                else: # Default to searching in the same module if no convention was matched for a separate impl module
                    target_impl_module_fqn = cls.__module__

            except TypeError as e: # inspect.getfile can raise TypeError for built-in modules/classes
                logger.error(f"  Could not determine module file for {cls.__name__}: {e}. Cannot find implementation by convention.")
                return None # Cannot proceed

            logger.debug(f"  Target FQN for implementation module: {target_impl_module_fqn}")

            # Step 2: Import the target module and find the Impl class
            found_impl_class = None
            if target_impl_module_fqn:
                try:
                    imported_module = importlib.import_module(target_impl_module_fqn)
                    logger.debug(f"  Successfully imported target implementation module: {target_impl_module_fqn}")

                    for name, obj in inspect.getmembers(imported_module):
                        if (inspect.isclass(obj) and
                                obj is not cls and # Not the header class itself
                                Header._has_direct_base_subclass(obj, cls) and # Is a direct subclass of the header
                                getattr(obj, '__class_type__', None) == Header.ClassType.Impl): # Is marked as Impl
                            
                            if found_impl_class is not None:
                                # More than one Impl class found for this header in the target module
                                logger.warning(
                                    f"  Multiple implementation classes found for {cls.__name__} in module {target_impl_module_fqn}: "
                                    f"{found_impl_class.__name__} and {obj.__name__}. Using the first one found."
                                )
                                # Or, optionally, raise an error:
                                # raise RuntimeError(f"Multiple Impl classes for {cls.__name__} in {target_impl_module_fqn}")
                            else:
                                logger.debug(f"    Found matching implementation class: {obj.__module__}.{obj.__name__}")
                                found_impl_class = obj
                                # Optionally break here if only one is expected per module
                                # break 
                
                except ImportError:
                    logger.warning(f"  Could not import target implementation module: {target_impl_module_fqn}")
                except Exception as e: # Catch other potential errors during import/inspection
                    logger.error(f"  Error inspecting module {target_impl_module_fqn} for implementation of {cls.__name__}: {e}")

            if found_impl_class:
                return found_impl_class
            else:
                logger.warning(f"  No implementation class found for {cls.__name__} in {target_impl_module_fqn} by convention.")
                return None
        
        # We should never get here, but just in case
        raise RuntimeError(f"Header {cls.__name__} is undefined type, don't know how to find implementation")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)