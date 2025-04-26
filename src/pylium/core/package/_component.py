from typing import Dict, Any, Optional, ClassVar, TypeVar, Generic, Type
from abc import ABC

# TODO: add dep to installer
from sqlalchemy import MetaData
from sqlmodel import SQLModel, Field

class _PackageComponent(SQLModel, table=False):
    """
    This is the base class for all Pylium components.
    It is used to register components and create a registry of components.

    Usually users will not need to use this class directly and instead use the ready built components in the package.
    If you need to create a new component, you can inherit from this class and add it to the registry.    
    """

    Field = Field

    # *** subclass overrides ***

    # The name of the component - used to register the component (set once per inheritance hierarchy)
    __component__ = ""

    # *** class attributes ***
    __registry__: Dict[str, type] = {}  # Global registry of all components

    @classmethod
    def __init_subclass__(cls, **kwargs):
        print(f"Component init_subclass: {cls.__name__}")
        super().__init_subclass__(**kwargs)
            
        # Handle __component__ - only inherit if set in parent. do only set once per inheritance hierarchy
        if cls.__component__ == "":
            # Check if any parent has set it
            for base in cls.__bases__:
                if hasattr(base, '__component__') and base.__component__ != "":
                    cls.__component__ = base.__component__
                    break

    @classmethod
    def register(cls):
        if not cls.__component__:
            raise ValueError("__component__ must be set for the component to be registered.")

        if cls.__component__ in cls.__registry__:
            raise ValueError(f"Component {cls.__component__} already registered by {cls.__registry__[cls.__component__].__name__}. Maybe forgot to set __component__ in the class {cls.__name__}?")

        cls.__registry__[cls.__component__] = cls

    @classmethod
    def get_component(cls, component_type: str) -> Optional[type]:
        """Get a component by its type"""
        return cls.__registry__.get(component_type)

    @classmethod
    def _get_component_info(cls, self = None) -> str:
        """Internal method to get component information."""
        component_inst_str = "object" if self is not None else "class"
        component_type = f"<{cls.__component__}>" or "<none>"
        # Check model config for table parameter
        table_is_true = "True" if getattr(cls, 'model_config', {}).get('table', False) else "False"

        component_type_registered = cls.get_component(cls.__component__)
        component_type_is_registered: bool = (component_type_registered is not None and issubclass(component_type_registered, cls))
        registry_status = "registered = True" if component_type_is_registered else "registered = False"
        
        table_name = cls.__tablename__ if hasattr(cls, '__tablename__') else '<none>'
        fields = cls.__fields__.keys()

        none_str = "<>"
        values = {}
        if self is not None:
            none_str = "<none>"
            for field in fields:
                values[field] = getattr(self, field)

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

    def __init__(self):
        print(f"Component init: {self.__module__}")
        super().__init__()

    def __repr__(self) -> str:
        """Returns a concise technical representation of the component."""
        table_is_true = "True" if getattr(self.__class__, 'model_config', {}).get('table', False) else "False"
        component_type = self.__component__ or "unregistered"
        return f"[{'✓' if table_is_true == 'True' else ' '}] {self.__class__.__name__} <{component_type}>"

    def __str__(self) -> str:
        return self._get_component_info(self)

        
