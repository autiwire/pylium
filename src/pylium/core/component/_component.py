from ._model import Model
from ._component_meta import ComponentMetaclass
from ._impl import ComponentImplMixin 

from typing import Type, ClassVar
import logging

logger = logging.getLogger(__name__)

# Add Model to the base classes here
class Component(Model, metaclass=ComponentMetaclass, table=False):
    """
    Base class for Pylium components, inheriting Model -> SQLModel.
    """

    ImplMixin: ClassVar[ComponentImplMixin] = ComponentImplMixin

    def __init__(self, *args, **kwargs):
        logger.debug(f"Component __init__: {self.__class__.__name__}")
        try:
            # super() will call Model.__init__ -> SQLModel.__init__
            super().__init__(*args, **kwargs)
        except TypeError as e:
            # This might happen if the configured_base has an __init__ with a
            # different signature and it's the next in the MRO chain.
            logger.warning(f"Potential issue during super().__init__ in {self.__class__.__name__}: {e}. Args: {args}, Kwargs: {kwargs}")
            # Decide how to handle this - maybe reraise, maybe log and continue?

    def __new__(cls, *args, **kwargs):
        logger.debug(f"Component __new__: {cls.__name__}")
        return super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        logger.debug(f"Component __init_subclass__: {cls.__name__}")
        # Use standard super() call for __init_subclass__
        super().__init_subclass__(**kwargs)
        

    # Add other common Component methods/attributes here if needed
    pass

    