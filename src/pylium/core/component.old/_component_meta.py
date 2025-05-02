from pylium.core.database._model_meta import _ModelMetaclass

from typing import Type
import logging

logger = logging.getLogger(__name__)

class _ComponentMetaclass(_ModelMetaclass):
    """
    Metaclass for Pylium Components, building upon ModelMetaclass.
    (Currently contains no Component-specific logic beyond inheriting ModelMetaclass).
    """

    # Simplified __new__: Removed is_impl logic and parameter.
    def __new__(mcls, name, bases, namespace, *args, **kwargs):
        new_cls = super().__new__(mcls, name, bases, namespace, *args, **kwargs)
        logger.debug(f"Class '{name}' created by _ComponentMetaclass: {new_cls}")

        # Any additional Component-specific setup on new_cls can go here

        return new_cls
    

