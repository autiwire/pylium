from typing import Type

import logging
logger = logging.getLogger(__name__)

class _ComponentMetaclass(type):
    """
    Metaclass for Pylium Components
    """
    
    def __new__(mcls, name, bases, namespace, *args, **kwargs):
        
        namespace["_is_impl"] = namespace.get("_is_impl", False)

        # create the object
        new_cls = super().__new__(mcls, name, bases, namespace, *args, **kwargs)
        logger.debug(f"Class '{name}' created by _ComponentMetaclass ({namespace['_is_impl']=}): {new_cls}")
        return new_cls
    

