"""
This module contains the base class for all headers.

A header is a class that contains the metadata for a module
and is used to load the implementation of the class.

Example: 

Modules structure:

project/package/module1.py -> Bundle
project/package/module1_h.py -> Header
project/package/module1_impl.py -> Impl File

 - or - 

project/module1/__init__.py -> Bundle
project/module1/__header__.py -> Header
project/module1/__impl__.py -> Impl File

Class Structure:

Header Class of the Module: Module1 @ module1_h.py or Module1 @ __header__.py
Impl Class of the Module: Module1Impl @ module1_impl.py or Module1Impl @ __impl__.py

Inheritance Chain (Parent -> Child):

Header -> Module1 -> Module1Impl (with __class_type__ = HeaderClassType.Impl)

When Module1 is imported, the headers is loaded, but not the implementation. 
The Impl File is loaded only when the Module1 is instantiated.

"""

from pylium.core import __manifest__ as __parent_manifest_
from pylium.manifest import Manifest

from abc import ABC, ABCMeta
import enum
from typing import Optional, Type
import importlib
import inspect
from pathlib import Path
import threading
import functools

import logging
logger = logging.getLogger(__name__)

__manifest__: Manifest = __parent_manifest_.createChild(
    location=Manifest.Location(module=__name__, classname=None),
    description="Header module",
    status=Manifest.Status.Development,
    dependencies=[],
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__parent_manifest_.authors.rraudzus, 
                                 notes=["Initial release"]),
        Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=__parent_manifest_.authors.rraudzus, 
                                 notes=["Added __manifest__ for module"]),
        Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,6,8), author=__parent_manifest_.authors.rraudzus,
                                 notes=["Enhanced CLI integration and discoverability",
                                        "Added @expose decorator for marking functions as CLI-accessible",
                                        "Improved Header class visibility checking in CLI tree building",
                                        "Enhanced manifest resolution for dual file pattern support",
                                        "Header classes now properly categorized in CLI CLASS sections",
                                        "Fixed recursive CLI navigation for consistent Header class discovery"]),
        Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,6,11), author=__parent_manifest_.authors.rraudzus,
                                 notes=["Added __parent_manifest_ to the header module manifest to allow for proper manifest resolution",
                                        "More explicitness and readability for AI: Use __manifest__ : Manifest = ... instead of __manifest__ = ..."]),
    ]
)

class classProperty(object):
    """
    Read-only class property decorator.
    Allows accessing a class method like a property (e.g., `ClassName.property`).
    """
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, owner):
        return self.fget(owner)

def dlock(lock_attr, instance_attr):
    """
    Decorator for thread-safe, lazy initialization using double-checked locking.

    This decorator wraps a *creator* method. It uses attributes on the class
    for the lock and for caching the created instance.
    """
    def decorator(creator_method):
        @functools.wraps(creator_method)
        def wrapper(cls, *args, **kwargs):
            instance = getattr(cls, instance_attr, None)
            if instance is None:
                lock = getattr(cls, lock_attr)
                with lock:
                    instance = getattr(cls, instance_attr, None)  # Double-check
                    if instance is None:
                        instance = creator_method(cls, *args, **kwargs)
                        setattr(cls, instance_attr, instance)
            return instance
        return wrapper
    return decorator

class HeaderClassType(enum.Enum):
    """
    Enum for the type of header class.
    """
    Undefined = "undefined"
    Header = "header"
    Impl = "impl"
    Bundle = "bundle" # Bundle is Header + Impl combined

class HeaderMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        

class Header(ABC, metaclass=HeaderMeta):
    """
    Base class for all headers.
    """

    ClassType = HeaderClassType.Header
    Manifest = Manifest
    
    __manifest__: Manifest = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="Base class for all headers",
        status=Manifest.Status.Development,
        dependencies=[],
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__parent_manifest_.authors.rraudzus, 
                                 notes=["Initial release"]),
            Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=__parent_manifest_.authors.rraudzus, 
                                 notes=["Added maintainers pointing to authors of the project"]),
            Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=__parent_manifest_.authors.rraudzus,
                                 notes=["Added license pointing to project license"]),
            Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,5,21), author=__parent_manifest_.authors.rraudzus, 
                                 notes=["Creating manifest as child of project manifest now"]),
            Manifest.Changelog(version="0.1.4", date=Manifest.Date(2025,5,25), author=__parent_manifest_.authors.rraudzus, 
                                 notes=["Added __class_type__ to the header class"]),
            Manifest.Changelog(version="0.1.5", date=Manifest.Date(2025,6,8), author=__parent_manifest_.authors.rraudzus,
                                 notes=["Improved CLI discoverability and navigation",
                                        "Header base class now properly appears in CLI CLASS sections",
                                        "Enhanced subclass detection for CLI tree building",
                                        "Fixed visibility rules to include Header alongside locally defined classes",
                                        "Better integration with recursive CLI navigation system"]),
        ]
    )
        
    __class_type__: HeaderClassType = HeaderClassType.Header

    # Set to a custom implementation class name if required
    # If not set the implementation will be automatically determined
    # by finding a direct child with __class_type__ = HeaderClassType.Impl
    __implementation__: Optional[str] = None

    @classmethod
    def _find_impl(cls_header) -> Optional[Type["Header"]]:
        """
        Find the implementation class for this specific header class (cls_header).
        Delegates the actual search logic to HeaderImpl._find_impl.
        """
        from .__impl__ import HeaderImpl 
        return HeaderImpl._find_impl(specific_header_cls=cls_header)

   
    def __init__(self, *args, **kwargs):
        logger.debug(f"Component __init__: {self.__class__.__name__} called with args: {args}, kwargs: {kwargs}")
        # Since Header is a direct subclass of ABC, and ABC.__init__ (which is object.__init__)
        # does not accept arbitrary *args, **kwargs, we call super().__init__() without them
        # to prevent the TypeError. Subclasses of Header are responsible for handling
        # their own arguments and calling their super().__init__ appropriately.
        super().__init__() # Changed from super().__init__(*args, **kwargs)


    def __new__(cls, *args, **kwargs):
        logger.debug(f"Component __new__: {cls.__name__} called with args: {args}, kwargs: {kwargs}")
   
        actual_class_to_instantiate = cls._find_impl()

        if not actual_class_to_instantiate:
            raise RuntimeError(
                f"Could not find or resolve an implementation for Header class {cls.__name__}. "
                f"Ensure an Impl class is defined by convention, or __implementation__ is set correctly, "
                f"or the class is a Bundle/Impl type."
            )

        logger.debug(f"  Actual class to instantiate determined by __new__ for {cls.__name__} is: {actual_class_to_instantiate.__name__}")
        instance = super().__new__(actual_class_to_instantiate)
        return instance


    def __init_subclass__(cls, **kwargs):
        logger.debug(f"Component __init_subclass__: {cls.__name__}")

        super().__init_subclass__(**kwargs)


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

