from typing import Dict, Any, Optional, ClassVar, TypeVar, Generic, Type
from abc import ABC

# TODO: add dep to installer
from sqlalchemy import MetaData
from sqlmodel import SQLModel, Field

class _PackageComponent(SQLModel):
    """
    This is the base class for all Pylium components.
    It is used to register components and create a registry of components.

    Usually users will not need to use this class directly and instead use the ready built components in the package.
    If you need to create a new component, you can inherit from this class and add it to the registry.    
    """

    Field = Field

    # *** subclass overrides ***

    # Abstract class - determines if this can be initialized (per-class)
    __abstract__ = True  # Base class is abstract, prevents table creation

    # The name of the component - used to register the component (set once per inheritance hierarchy)
    __component__ = ""

    # *** class attributes ***
    __registry__: Dict[str, type] = {}  # Global registry of all components

    def __init_subclass__(cls, **kwargs):
        print(f"Component init_subclass: {cls.__name__}")
        super().__init_subclass__(**kwargs)
        
        # Handle __abstract__ - each class decides for itself
        if '__abstract__' not in cls.__dict__:
            print(f"Component init_subclass: {cls.__name__} __abstract__ not set")
            cls.__abstract__ = False  # Concrete classes get tables by default
            
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
    def _get_component_info(cls) -> str:
        """Internal method to get component information."""
        component_type = f"<{cls.__component__}>" or "<>"
        abstract_status = "abstract = True" if cls.__abstract__ else "abstract = False"
        registry_status = "registered = True" if component_type in cls.__registry__ else "registered = False"
        
        return (
            f"  Module: {cls.__module__}\n"
            f"  Component: {component_type}\n"
            f"  Status: {abstract_status}, {registry_status}"

        )

    @classmethod
    def __info__(cls) -> str:
        """Returns a human-readable string representation of the component class."""
        return f"<class {cls.__name__}>:\n{cls._get_component_info()}"

    def __new__(cls, *args, **kwargs):
        print(f"Component new: {cls.__module__}")
        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        print(f"Component init: {self.__module__}")
        super().__init__()

    def __repr__(self) -> str:
        """Returns a concise technical representation of the component."""
        component_type = self.__component__ or "unregistered"
        abstract = "A" if self.__abstract__ else "C"  # A for Abstract, C for Concrete
        registered = "R" if component_type in self.__registry__ else "U"  # R for Registered, U for Unregistered
        return f"<{self.__class__.__name__} {component_type} {abstract}{registered}>"

    def __str__(self) -> str:
        """Returns a human-readable string representation of the component."""
        sqlmodel_str = super().__str__()
        component_info = self._get_component_info()
        table_name = self.__class__.__tablename__ if hasattr(self.__class__, '__tablename__') else 'no table'
        
        # Split SQLModel string into individual fields
        fields = sqlmodel_str.strip('{}').split(', ')
        
        return (
            f"<{self.__class__.__name__} instance>:\n"
            f"{component_info}\n"
            f"  SQLModel: {table_name}\n"
            + '\n'.join(f"    {field}" for field in fields)
        )

        
