from pylium.core.package import Package
from pylium.core.module import Module
from ._base import ComponentBase
from ._meta import ComponentMetaclass

from typing import Type, ClassVar, List
import os
import importlib
import inspect

# Import the heavy machinery
#
# Here you would import the heavy machinery, but do it in the impl module instead
# Here we only define the dependencies of the compontent for the install system to detect them automatically
#

class ComponentPackageHeader(Package):
    """
    Package for Pylium component headers
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version=Manifest.Version("0.0.1"), since_date=Package.Date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version=Manifest.Version("0.0.1"), notes=["Initial release"], date=Package.Date(2025, 5, 10)),
    ]

logger = ComponentPackageHeader.logger

class Component(ComponentBase, metaclass=ComponentMetaclass):
    """
    Base class for Pylium components

    Inherit from this class to create a component header.

    The component header is the public interface of a component.
    It is used to define the component's dependencies and to find the implementation.

    The component implementation is a separate class that is used to implement the component.
    It is marked with a _impl suffix or name and is located in the same directory as the header.

    The component implementation must inherit from the component header.
    The component implementation must be marked with the _is_impl flag.

    The component header and implementation must be in the same package/module/project/directory.
    """

    Base = ComponentBase
    Metaclass = ComponentMetaclass

    @classmethod
    def _version(cls) -> str:
        """
        Get the version of the module of the component.
        """
        mod = cls._module()
        if not mod is None:
            return mod.version
        return None
    
    @classmethod
    def _name(cls) -> str:
        """
        Get the name of the module of the component.
        """
        mod = cls._module()
        if not mod is None:
            return mod.name
        return None

    @classmethod
    def _module(cls) -> Type[Module]:
        """
        Get the module of the component.
        """
        module_name_str = cls.__module__ # Get the string name of the module
        try:
            module_obj = importlib.import_module(module_name_str)
        except ImportError:
            logger.error(f"Could not import module {module_name_str} to find the Module class.")
            raise RuntimeError(f"Could not import module {module_name_str} to find the Module class.")

        ret_mod = None
        # Iterate over members of the actual module object
        for name, obj in inspect.getmembers(module_obj):
            # logger.debug(f"  Checking member: {name} ({type(obj)}) in module {module_name_str}")
            if inspect.isclass(obj) and obj is not Module and issubclass(obj, Module):
                # Ensure the class is defined in this module, not imported from elsewhere
                if obj.__module__ == module_name_str:
                    if ret_mod is not None:
                        logger.error(f"Multiple classes inheriting from Module found in {module_name_str}: {ret_mod.__name__} and {obj.__name__}")
                        raise RuntimeError(f"Multiple classes inheriting from Module found in {module_name_str}: {ret_mod.__name__} and {obj.__name__}")
                    ret_mod = obj
            
        if ret_mod is None:
            logger.error(f"No class inheriting from Module found in {module_name_str}")
            raise RuntimeError(f"No class inheriting from Module found in {module_name_str}")
        return ret_mod

    # Find the implementation class for this component
    @classmethod
    def _find_impl(cls) -> Type["Component"]:
        """
        Find the implementation class for this component.
        """

        # get the module of the component
        my_module = cls._module()

        logger.debug(f"  Found module: {my_module}")

        if my_module is not None:
            logger.debug(f"  Module: {my_module}")
        else:
            logger.warning(f"  Did not find ModuleClass for {cls.__name__}")
            return None

        my_impl_module_class = my_module.get_implementation_module_class()
        logger.debug(f"  Found Implementation ModuleClass: {my_impl_module_class}")
        if my_impl_module_class is None:
            logger.warning(f"  Did not find Implementation ModuleClass for {cls.__name__}")
            return None

        # Now we got module/ModuleClass of the Implementation Module
        # We need to find the class in the implementation module
        # that is a subclass of the component class

        impl_modules_names = [ my_impl_module_class.__module__ ]
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