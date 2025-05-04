"""
Pylium Core Components

This module contains the base classes for core components of Pylium.

The Component class is the base class for all Pylium components.

"""

from ._meta import ComponentMetaclass
from ._base import ComponentBase
from ._module import ComponentModule

from typing import Type, ClassVar, Optional, List
import datetime

# Import the heavy machinery
#
# Here you would import the heavy machinery, but do it in the impl module instead
# Here we only define the dependencies of the compontent for the install system to detect them automatically
#

import importlib
import inspect
import os

pylium = ComponentModule(
    name=__name__,
    version="0.1.0",
    description="Pylium component",
    dependencies=[
        ComponentModule.Dependency(name="pydantic-settings", type=ComponentModule.Dependency.Type.PIP, version=">=0.1.0"),
        ComponentModule.Dependency(name="fire", type=ComponentModule.Dependency.Type.PIP, version=">=0.5.0")
    ],
    authors=[
        ComponentModule.AuthorInfo(name="John Doe", email="john.doe@example.com", since_version="0.1.0", since_date=datetime.date(2021, 1, 1))
    ],
    settings_class=ComponentModule.Config,
    cli=True,
)
logger = pylium.logger

class Component(ComponentBase, metaclass=ComponentMetaclass):
    """
    Base class for Pylium core components
    """

    Base = ComponentBase
    Metaclass = ComponentMetaclass
    Module = ComponentModule

    # Calculate the likely source root by going up 3 levels from the current file's directory
    _current_file_dir = os.path.dirname(__file__)
    _default_src_root = os.path.abspath(os.path.join(_current_file_dir, '..', '..', '..'))

    # Calculate ComponentDirs based on environment variable or default src root
    _env_dirs_str = os.environ.get("PYLIUM_COMPONENT_DIRS")
    _component_src_roots = []  # Initialize as empty list

    if _env_dirs_str:
        # If env var is set, split using os.pathsep and filter out empty/whitespace-only paths
        _component_src_roots = [
            d.strip() for d in _env_dirs_str.split(os.pathsep) if d.strip()
        ]

    # If the environment variable didn't provide any valid paths, use the calculated default
    if not _component_src_roots:
        _component_src_roots = [_default_src_root]
    # Optional: Uncomment below if you ALWAYS want to include the default src root
    # elif _default_src_root not in _component_src_roots:
    #    _component_src_roots.insert(0, _default_src_root) # Prepend default root

    ComponentDirs: ClassVar[List[str]] = _component_src_roots

    @classmethod
    def _find_impl(cls) -> Type["Component"]:
        my_module = cls.__module__
        # FIX: Generate correct relative name like 'pylium.core.component._impl'
        impl_modules_names = [
            f"{my_module}",               # Check module itself
            f"{my_module}_impl",          # Check sibling_impl.py (e.g., core/component_impl.py)
            f"{my_module}._impl"          # Check _impl.py inside package (e.g., component/_impl.py)
        ]

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
                        break  # Found the class in this module, exit inner loop

            except ImportError:
                logger.debug(f"  Could not import potential impl module: {module_name}")
                continue  # Skip if module doesn't exist
            except Exception as e:  # Catch other potential errors during import/inspection
                logger.warning(f"  Error inspecting module {module_name}: {e}")
                continue

            if impl_cls:
                break  # Found the class, exit outer loop

        if not impl_cls:
            logger.debug(f"  No implementation class found after searching: {impl_modules_names}")

        return impl_cls

    @staticmethod
    def _get_all_component_modules(skip_impl: bool = True) -> List[ComponentModule]:
        logger.debug(f"Searching for component modules in roots: {Component.ComponentDirs}")
        component_modules: List[ComponentModule] = []

        for root_dir in Component.ComponentDirs:
            if not os.path.isdir(root_dir):
                logger.warning(f"Component source root directory not found: {root_dir}")
                continue

            # Ensure root_dir is absolute for correct path joining
            root_dir = os.path.abspath(root_dir)
            logger.debug(f"Walking directory: {root_dir}")

            for subdir, dirs, files in os.walk(root_dir):
                # Optional: Skip hidden directories or specific patterns like .venv, .git, __pycache__
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

                for file in files:
                    if not file.endswith(".py"): # or file == '__init__.py':
                        continue

                    base_module_name = file[:-3]

                    # Skip impl files if requested
                    if skip_impl and base_module_name.endswith("_impl"):
                        continue

                    # Construct the full Python module path
                    try:
                        full_file_path = os.path.join(subdir, file)
                        potential_src_root = root_dir # Assuming root_dir is the correct base
                        relative_path = os.path.relpath(full_file_path, potential_src_root)
                        module_path_parts = relative_path[:-3].split(os.sep)
                        full_module_path = ".".join(module_path_parts)
                    except ValueError:
                        logger.warning(f"Could not determine relative path for {full_file_path} from {potential_src_root}")
                        continue

                    if full_module_path.endswith("__init__"):
                        # remove the __init__ part
                        full_module_path = full_module_path[:-9]

                    logger.debug(f"Attempting to import: {full_module_path}")
                    try:
                        module = importlib.import_module(full_module_path)
                        logger.debug(f"Successfully imported module: {full_module_path}")

                        # Check if module has pylium attribute and it is a ComponentModule instance
                        if hasattr(module, "pylium"):
                            if isinstance(module.pylium, ComponentModule):
                                logger.debug(f"Found ComponentModule (pylium) in: {full_module_path}")
                                component_modules.append(module.pylium)
                            else:
                                logger.warning(f"Found pylium in {full_module_path}, but it is not a ComponentModule instance.")

                    except ImportError as e:
                        logger.debug(f"Could not import module {full_module_path} (might not be a valid module): {e}")
                    except Exception as e:
                        logger.error(f"Error processing module {full_module_path}: {e}", exc_info=True)

        logger.info(f"Found {len(component_modules)} component modules.")
        return component_modules
   
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
    
__all__ = ["Component"]