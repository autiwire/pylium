from typing import Type

import logging
logger = logging.getLogger(__name__)

class ComponentMetaclass(type):
    """
    Metaclass for Pylium Components
    """
    
    def __new__(mcls, name, bases, namespace, *args, **kwargs):
        new_cls = super().__new__(mcls, name, bases, namespace, *args, **kwargs)
#        logger.debug(f"Class '{name}' created by _ComponentMetaclass ({namespace['_is_impl']=}): {new_cls}")
        return new_cls
    

