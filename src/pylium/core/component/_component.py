from ._meta import ComponentMetaclass
from ._impl import ComponentImplMixin 
from ._database import SQLModel

from typing import Type, ClassVar
import logging

logger = logging.getLogger(__name__)

# Component now only uses the metaclass, SQLModel is injected by the meta
class Component(metaclass=ComponentMetaclass):
    """
    Base class for Pylium components.

    Inherits dynamically from a specific SQLModel base class specified by the
    'sqlmodel_base' keyword argument during class definition (defaults to SQLModel).
    """

    Meta: ClassVar[ComponentMetaclass] = ComponentMetaclass
    ImplMixin: ClassVar[ComponentImplMixin] = ComponentImplMixin

    def __init__(self, *args, **kwargs):
        logger.debug(f"Component __init__: {self.__class__.__name__}")
        try:
            # Super call will now correctly find the injected SQLModel base
            super().__init__(*args, **kwargs)
        except TypeError as e:
            # This might happen if the configured_base has an __init__ with a
            # different signature and it's the next in the MRO chain.
            logger.warning(f"Potential issue during super().__init__ in {self.__class__.__name__}: {e}. Args: {args}, Kwargs: {kwargs}")
            # Decide how to handle this - maybe reraise, maybe log and continue?

    def __new__(cls, *args, **kwargs):
        logger.debug(f"Component __new__: {cls.__name__}")
        # Standard __new__ behavior unless overridden by subclasses 
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        logger.debug(f"Component __init_subclass__: {cls.__name__}")
        super().__init_subclass__(**kwargs)
        

    # Add other common Component methods/attributes here if needed
    pass

    