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

from pylium import __project__
from pylium.core.manifest import Manifest

from abc import ABC, ABCMeta
import enum
from typing import Optional, Type
import importlib
import inspect
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

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
    
    __manifest__: Manifest = __project__.__manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="Base class for all headers",
        status=Manifest.Status.Development,
        dependencies=[],
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Initial release"]),
            Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Added maintainers pointing to authors of the project"]),
            Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Added license pointing to project license"]),
            Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,5,21), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Creating manifest as child of project manifest now"]),
            Manifest.Changelog(version="0.1.4", date=Manifest.Date(2025,5,25), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Added __class_type__ to the header class"])
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

