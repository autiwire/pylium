# Placed in tests/core/demo_h.py
from pylium.core.header.__header__ import Header, HeaderClassType # Adjusted import

import logging
logger = logging.getLogger(__name__)

class DemoH(Header):
    __class_type__ = HeaderClassType.Header
    # Explicitly point to the Impl class now that it's in the tests directory
    __implementation__ = "tests.core.demo_impl.DemoI" 

    STATIC_VAR_HEADER = "Defined in DemoH"

    def __init__(self, name: str, value: int, **kwargs): # Added **kwargs
        super().__init__(name=name, value=value, **kwargs) # Pass along args
        self.name_h = name
        self.value_h = value
        logger.info(f"DemoH ({self.__class__.__name__}) __init__ called for {self.name_h}")

    def header_method(self):
        logger.info(f"DemoH ({self.__class__.__name__}) header_method called for {self.name_h}")
        return f"Header method from DemoH: {self.name_h}"

    @classmethod
    def header_class_method(cls):
        logger.info(f"DemoH class_method called on cls: {cls.__name__}")
        return f"Class method from DemoH (called on {cls.__name__}), static var: {hasattr(cls, 'STATIC_VAR_HEADER') and cls.STATIC_VAR_HEADER}" 