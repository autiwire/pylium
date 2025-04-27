from typing import Dict, Any, Optional, ClassVar, TypeVar, Generic, Type, List

# TODO: add dep to installer
from sqlmodel import SQLModel, Field
import importlib
import os

class _PackageComponent():
    """
    This is the base class for all Pylium components.
    """

    Field = Field

    # *** subclass overrides ***

    # The name of the component - used to register the component (set once per inheritance hierarchy)
    __component__: str = ""

    # *** class attributes ***

    # Global registry of all components
    __registry__: Dict[str, type] = {} 

    # *** class methods ***
    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        print(f"Component init_subclass: {cls.__name__}")
        # Don't call super().__init_subclass__ as object doesn't accept args
        # super().__init_subclass__(*args, **kwargs)
            
        # Handle __component__ - only inherit if set in parent. do only set once per inheritance hierarchy
        if cls.__component__ == "":
            # Check if any parent has set it
            for base in cls.__bases__:
                if hasattr(base, '__component__') and base.__component__ != "":
                    cls.__component__ = base.__component__
                    break

    def __init__(self, *args, **kwargs):
        print(f"Component init: {self.__module__}")
        # Don't call super().__init__ as we need to handle SQLModel initialization
        # super().__init__(*args, **kwargs)

    @classmethod
    def register(cls):
        if not cls.__component__:
            raise ValueError("__component__ must be set for the component to be registered.")

        if cls.__component__ in cls.__registry__:
            raise ValueError(f"Component {cls.__component__} already registered by {cls.__registry__[cls.__component__].__name__}. Maybe forgot to set __component__ in the class {cls.__name__}?")

        cls.__registry__[cls.__component__] = cls

    @classmethod
    def get_component(cls, component_type: str) -> Optional[type]:
        """Get a component by its component type"""
        return cls.__registry__.get(component_type)


    # Get the component of the package the class is in, defined by its base class
    # Therefore get the __component__ of the base class and store it into a string component_type
    # Search for _{component_type} package/module and return the class inheriting from component_base_class
    @classmethod
    def get_sibling_component(cls, sibling_class: type) -> Optional[type]:
        """Get a component type from the same module/package"""
        
        print(f"Getting sibling component for {sibling_class.__name__} of class {cls.__name__}")
        
        # Don't look for siblings if we're already an implementation class
        if issubclass(cls, sibling_class):
            return None
            
        module_name = cls.__module__
        # Module names can have 2 schemes:
        # a/b/c/_{component_type}.py
        # a/b/c_{component_type}.py
        # We need to extract the package name from the module name
        package_parts = module_name.split('.')
        
        # Get the component type from the sibling class
        component_type = sibling_class.__component__
        if not component_type:
            return None
            
        # Get the current module name without the component type
        base_module = '_'.join(package_parts[-1].split('_')[:-1])
        if not base_module:
            base_module = package_parts[-1]
        print(f"Base module: {base_module}")
        
        # Determine which scheme we're using
        current_module = package_parts[-1]
        if current_module.startswith('_'):
            # Style 1: a/b/c/_{component_type}.py
            module_path = '.'.join(package_parts[:-1] + [f"_{component_type}"])
        else:
            # Style 2: a/b/c_{component_type}.py
            module_path = '.'.join(package_parts[:-1] + [f"{base_module}_{component_type}"])
            
        print(f"Module path: {module_path}")
        
        try:
            module = importlib.import_module(module_path)
            print(f"Module: {module}")
            
            # Use pkgutil to find the class that inherits from sibling_class
            import pkgutil
            import inspect
            
            # Get all classes in the module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj != cls:  # Skip the current class
                    print(f"Found class: {name}")
                    if issubclass(obj, sibling_class):
                        print(f"Found component: {obj.__name__}")
                        return obj
                        
        except ImportError:
            print(f"No component module {module_path} found")
            return None

    @classmethod
    def _get_component_info(cls, self = None) -> str:
        """Internal method to get component information."""
        component_inst_str = "object" if self is not None else "class"
        component_type = f"<{cls.__component__}>" or "<none>"
        component_type_registered = cls.get_component(cls.__component__)
        component_type_is_registered: bool = (component_type_registered is not None and issubclass(component_type_registered, cls))
        registry_status = "registered = True" if component_type_is_registered else "registered = False"
        
        table_is_true = "True" if getattr(cls, 'model_config', {}).get('table', False) else "False"
        table_name = cls.__tablename__ if hasattr(cls, '__tablename__') else '<none>'
        fields = cls.__fields__.keys()

        print(f"Fields: {fields}")

        none_str = "<>"
        values = {}
        if self is not None:
            none_str = "<none>"
            for field in fields:
                values[field] = self.__getattr__(field)

        print(f"Values: {values}")

        ret_str = (
            f"[{'✓' if table_is_true == 'True' else ' '}] {cls.__name__} <{component_inst_str}>\n"
            f"  Module: {cls.__module__}\n"
            f"  Component: {component_type}\n"
            f"  Status: {registry_status}\n"            
            f"  SQLModel: {table_name}\n"
            + '\n'.join(f"    {field}: {values.get(field, none_str)}" for field in fields)
        ).strip()
        return ret_str

    @classmethod
    def __info__(cls) -> str:
        """Returns a human-readable string representation of the component class."""
        return cls._get_component_info()

    def __new__(cls, *args, **kwargs):
        print(f"Component new: {cls.__module__}")
        return super().__new__(cls, *args, **kwargs)

    def __repr__(self) -> str:
        """Returns a concise technical representation of the component."""
        table_is_true = "True" if getattr(self.__class__, 'model_config', {}).get('table', False) else "False"
        component_type = self.__component__ or "<none>"
        return f"[{'✓' if table_is_true == 'True' else ' '}] {self.__class__.__name__} <{component_type}>"

    def __str__(self) -> str:
        return self._get_component_info(self)

class _PackageHeaderComponent(_PackageComponent, SQLModel, table=False):
    """
    This is the base class for all Pylium components.
    It is used to register components and create a registry of components.

    Usually users will not need to use this class directly and instead use the ready built components in the package.
    If you need to create a new component, you can inherit from this class and add it to the registry.    
    """

    def __init__(self, *args, **kwargs):
        print(f"Header component init: {self.__module__}")
        # Initialize SQLModel first to ensure Pydantic is set up
        SQLModel.__init__(self, *args, **kwargs)
        # Then initialize the package component
        _PackageComponent.__init__(self, *args, **kwargs)

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        print(f"Header component init_subclass: {cls.__name__}")
        # Call SQLModel's __init_subclass__ first to ensure Pydantic is set up
        SQLModel.__init_subclass__()
        # Then call parent __init_subclass__
        _PackageComponent.__init_subclass__(cls)

class _PackageImplComponentMixin(_PackageComponent):
    """
    This is a mixin class for all Pylium implementation components.
    """

    def __init__(self, *args, **kwargs):
        print(f"Impl component init: {self.__module__}")
        # Initialize the package component
        _PackageComponent.__init__(self, *args, **kwargs)

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        print(f"Impl component init_subclass: {cls.__name__}")
        _PackageComponent.__init_subclass__(cls)