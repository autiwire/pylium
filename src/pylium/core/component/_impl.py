
import logging
logger = logging.getLogger(__name__)

class ComponentImplMixin():
    
    def __init__(self, *args, **kwargs):
        logger.debug(f"ComponentImplMixin __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        logger.debug(f"ComponentImplMixin __new__: {cls.__name__}")
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        logger.debug(f"ComponentImplMixin __init_subclass__: {cls.__name__}")
        super().__init_subclass__(**kwargs)


