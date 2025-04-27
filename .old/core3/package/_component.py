# Every single file in a package is a component
# The component baseclass is _Component in _component.py

# Compontents directly inheriting from _Component are package base components
# Their module filename will determine the module filenames for lookup of their children

from typing import ClassVar
from types import ModuleType

import logging
logger = logging.getLogger(__name__)
from threading import Lock

class Component():

    _class_logger_private: ClassVar[logging.LoggerAdapter] = None
    _class_logger_lock: ClassVar[Lock] = Lock()

    @classmethod
    def _logger(cls: type) -> logging.LoggerAdapter:
        """Gets the logger associated with this component class's module."""

        if cls._class_logger_private is None:
            with cls._class_logger_lock:
                if cls._class_logger_private is None:
                    print(f"DEBUG: Getting logger for {cls.__name__}")
                    my_cls_logger = logging.getLogger(cls.__module__)
                    my_cls_log_adapter = logging.LoggerAdapter(my_cls_logger, {"class_name": cls.__name__})
                    cls._class_logger_private = my_cls_log_adapter

        return cls._class_logger_private
    
    @staticmethod
    def has_direct_base_subclass(A: type, B: type) -> bool:
        """
        Returns True if A has B (or a subclass of B) as a direct base class.
        Handles potential TypeErrors if A.__bases__ is not available.
        """
        try:
             # Check direct bases only
             return any(base is B or (isinstance(base, type) and issubclass(base, B)) for base in A.__bases__)
        except AttributeError:
             print(f"Could not access __bases__ for type {A} during check.")
             return False

    @classmethod
    def get_sibling_from_basetype(cls: type, sibling_basetype: type) -> ModuleType:
        """
        Searches in the cls module path for a module that is called like the module from the sibling_basetype
        
        Example:
        cls: <module 'pylium.core.package._header' from '.../pylium/core/package/_header.py'>
        sibling_basetype: <class 'pylium.core.package.Package.Impl'>
        -> <module 'pylium.core.package._impl' from '.../pylium/core/package/_impl.py'>
        """

        # walk up the baseclass hierarchy until the baseclass is a Component
        real_sibling_basetype = sibling_basetype.get_basetype()
        
        # get the module path of the real_basetype
        real_basetype_module = real_sibling_basetype.__module__
        real_basetype_module_name = real_basetype_module.split(".")[-1]
        print(f"real_basetype_module: {real_basetype_module}")
        print(f"real_basetype_module_name: {real_basetype_module_name}")

        # get the module path of the cls and exchange the last part with the real_basetype_module_name
        base_module = cls.__module__
        base_module_name = base_module.split(".")[-1]
        print(f"base_module: {base_module}")
        print(f"base_module_name: {base_module_name}")
        sibling_module_name = base_module.replace(base_module_name, real_basetype_module_name)
        print(f"sibling_module_name: {sibling_module_name}")

        # check if the module exists without importing it
        module = None
        try:
            import importlib
            module = importlib.import_module(sibling_module_name)
        except ImportError:
            raise ValueError(f"Module {sibling_module_name} does not exist")

        # check if the module contains a class inheriting from the sibling_basetype
        sibling_class = None # Initialize sibling_class
        module_classes = module.__dict__.values()
        for item in module_classes:
            # Check if item is a class and is a subclass of sibling_basetype
            # issubclass() also returns True if item is sibling_basetype itself
            if isinstance(item, type) and item is not sibling_basetype and issubclass(item, sibling_basetype):
                sibling_class = item
                break # Found the first matching class

            # TODO: Check if other possible siblings exist in debug mode -> warning user of non-unique components

        # Check if a sibling class was found
        if sibling_class is None:
            raise ValueError(f"Module {sibling_module_name} does not contain a class inheriting from {sibling_basetype.__name__}")

        return sibling_class      

    @classmethod
    def get_basetype(cls) -> type:
        """
        Returns the base type of the component.
        """
        real_basetype = None
        current_cls = cls
        while current_cls is not None:
            if current_cls.has_direct_base_subclass(current_cls, Component):
                real_basetype = current_cls
                break
            current_cls = current_cls.__bases__[0]
        
        if real_basetype is None:
            raise ValueError(f"Could not find a base class of Component {cls.__name__} in the hierarchy of the given type")
        
        return real_basetype        
    
    def __init__(self, *args, **kwargs):
        print("Component __init__")

        # Get the logger for the component baseclass
        self._log = logging.LoggerAdapter(
            self.__class__._logger(),
            {'class_name': self.__class__.__name__}
        )

    def __new__(cls, *args, **kwargs):
        print("Component __new__")
        return super().__new__(cls, *args, **kwargs)



