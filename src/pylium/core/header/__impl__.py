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
    def _find_impl(cls, specific_header_cls: Type["Header"]) -> Type["Header"]:
        """
        Find the implementation class for the given specific_header_cls.
        'cls' here is HeaderImpl itself.
        """

        logger.debug(f"  HeaderImpl._find_impl searching for implementation of: {specific_header_cls.__name__} @ {specific_header_cls.__module__}")

        # Manual __implementation__ string on the specific_header_cls takes precedence
        # This attribute should be on the actual header class (e.g., MyModuleH.__implementation__)
        explicit_impl_fqn = getattr(specific_header_cls, '__implementation__', None)
        if explicit_impl_fqn:
            logger.debug(f"  {specific_header_cls.__name__} has manual implementation setting: {explicit_impl_fqn}")
            if not isinstance(explicit_impl_fqn, str):
                raise TypeError(f"__implementation__ attribute on {specific_header_cls.__name__} must be a string FQN.")
            
            module_name, class_name = explicit_impl_fqn.rsplit(".", 1)
            try:
                module = importlib.import_module(module_name)
                loaded_impl_class = getattr(module, class_name)
                
                # Validate the loaded class
                if getattr(loaded_impl_class, '__class_type__', None) != Header.ClassType.Impl:
                    raise TypeError(
                        f"Explicitly specified implementation class {explicit_impl_fqn} "
                        f"for {specific_header_cls.__name__} is not marked as {Header.ClassType.Impl}."
                    )
                if not issubclass(loaded_impl_class, Header): # Or perhaps issubclass(loaded_impl_class, specific_header_cls)
                     raise TypeError(
                         f"Explicitly specified implementation class {explicit_impl_fqn} "
                         f"for {specific_header_cls.__name__} must be a subclass of Header."
                     )
                logger.debug(f"  Successfully loaded and validated explicit implementation: {loaded_impl_class.__name__}")
                return loaded_impl_class
            except (ImportError, AttributeError, ValueError) as e: # ValueError for rsplit if not a valid FQN
                raise RuntimeError(
                    f"Could not load or validate specified implementation '{explicit_impl_fqn}' for {specific_header_cls.__name__}: {e}"
                )

        # Determine class type of the specific_header_cls we are trying to implement
        header_cls_type = getattr(specific_header_cls, '__class_type__', None)

        if header_cls_type == Header.ClassType.Bundle:
            logger.debug(f"  {specific_header_cls.__name__} is a Bundle, it is its own implementation.")
            return specific_header_cls
        
        elif header_cls_type == Header.ClassType.Impl:
            logger.debug(f"  {specific_header_cls.__name__} is an Impl, it is its own implementation.")
            return specific_header_cls
        
        elif header_cls_type == Header.ClassType.Header:
            logger.debug(f"  {specific_header_cls.__name__} is a Header, finding implementation by convention...")

            # Step 1: Determine the target implementation module name (using specific_header_cls)
            target_impl_module_fqn = None
            try:
                # Use specific_header_cls for path and module info
                header_module_path = Path(inspect.getfile(specific_header_cls))
                header_module_name_stem = header_module_path.stem
                # Use specific_header_cls.__module__ for its package path
                header_package_dot_path = '.'.join(specific_header_cls.__module__.split('.')[:-1])

                if header_module_name_stem == "__header__":
                    target_impl_module_stem = "__impl__"
                elif header_module_name_stem.endswith("_h"):
                    target_impl_module_stem = header_module_name_stem[:-2] + "_impl"
                else:
                    logger.warning(
                        f"  Header class {specific_header_cls.__module__}.{specific_header_cls.__name__} module filename '{header_module_path.name}' "
                        f"does not follow __header__.py or <name>_h.py convention. "
                        f"Will search for Impl in the same module ({specific_header_cls.__module__})."
                    )
                    target_impl_module_stem = None 

                if target_impl_module_stem:
                    if header_package_dot_path:
                        target_impl_module_fqn = f"{header_package_dot_path}.{target_impl_module_stem}"
                    else:
                        target_impl_module_fqn = target_impl_module_stem
                else: 
                    target_impl_module_fqn = specific_header_cls.__module__ # Search in header's own module

            except TypeError as e: 
                logger.error(f"  Could not determine module file for {specific_header_cls.__name__}: {e}. Cannot find implementation by convention.")
                return None 

            logger.debug(f"  Target FQN for convention-based implementation module: {target_impl_module_fqn}")

            # Step 2: Import the target module and find the Impl class
            found_impl_class_by_convention = None
            if target_impl_module_fqn:
                try:
                    imported_module = importlib.import_module(target_impl_module_fqn)
                    logger.debug(f"  Successfully imported target convention module: {target_impl_module_fqn}")

                    for name, obj in inspect.getmembers(imported_module):
                        # Use specific_header_cls as the base for subclass check
                        if (inspect.isclass(obj) and
                                obj is not specific_header_cls and 
                                Header._has_direct_base_subclass(obj, specific_header_cls) and 
                                getattr(obj, '__class_type__', None) == Header.ClassType.Impl): 
                            
                            if found_impl_class_by_convention is not None:
                                logger.warning(
                                    f"  Multiple convention-based implementation classes found for {specific_header_cls.__name__} in module {target_impl_module_fqn}: "
                                    f"{found_impl_class_by_convention.__name__} and {obj.__name__}. Using the first one found."
                                )
                            else:
                                logger.debug(f"    Found matching convention-based Impl class: {obj.__module__}.{obj.__name__}")
                                found_impl_class_by_convention = obj
                
                except ImportError:
                    logger.warning(f"  Could not import convention-based target implementation module: {target_impl_module_fqn}")
                except Exception as e: 
                    logger.error(f"  Error inspecting module {target_impl_module_fqn} for convention-based Impl of {specific_header_cls.__name__}: {e}")

            if found_impl_class_by_convention:
                return found_impl_class_by_convention
            else:
                # This path is reached if specific_header_cls is HeaderClassType.Header,
                # an __implementation__ FQN was NOT provided, and convention search failed.
                header_class_fqn = f"{specific_header_cls.__module__}.{specific_header_cls.__name__}"
                
                # Determine the original header file name for a more informative message
                header_file_path = Path(inspect.getfile(specific_header_cls))
                header_actual_file_name = header_file_path.name

                error_message = (
                    f"Component '{header_class_fqn}' (a Header) requires an Implementation, but none was found.\\n"
                    f"Convention-based search for an Impl class failed in module '{target_impl_module_fqn}' \\n"
                    f"(Note: This target module was derived from the Header's file name: '{header_actual_file_name}').\\n"
                    f"To resolve this, you can:\\n"
                    f"1. Define an Impl class (a subclass of '{specific_header_cls.__name__}' with '__class_type__ = Header.ClassType.Impl') \\n"
                    f"   within module '{target_impl_module_fqn}'. Ensure it follows naming conventions \\n"
                    f"   (e.g., place Impl in '__impl__.py' for a Header in '__header__.py', or in '<name>_impl.py' for '<name>_h.py').\\n"
                    f"2. Or, explicitly link to an existing Impl class by setting the '__implementation__' FQN attribute \\n"
                    f"   on the Header class '{specific_header_cls.__name__}'.\\n"
                    f"3. Or, if '{specific_header_cls.__name__}' is intended to be a self-contained component (without a separate Impl), \\n"
                    f"   change its '__class_type__' attribute to 'Header.ClassType.Bundle'."
                )
                logger.debug(f"No convention-based Impl found for Header '{header_class_fqn}'. Search was in '{target_impl_module_fqn}'. Raising RuntimeError.")
                raise RuntimeError(error_message)
        
        raise RuntimeError(f"Header {specific_header_cls.__name__} has an undefined __class_type__ or unhandled case in _find_impl.")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)