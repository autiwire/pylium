from ._component import Component

import logging
logger = logging.getLogger(__name__)

class ComponentImpl(Component):
    _is_impl = True

    def __init__(self, *args, **kwargs):
        logger.debug(f"ComponentImpl __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

