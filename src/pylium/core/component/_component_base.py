# Pylium Component Base


from typing import ClassVar

import logging
logger = logging.getLogger(__name__)

class ComponentBase:
    """
    Base class for Pylium core components
    """

    # Per-class implementation setting - set this to True in impl classes
    _is_impl: ClassVar[bool] = False # False by default -> header class, set to True in impl classes
    _no_impl: ClassVar[bool] = False # False by default -> disables loading of impl classes

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

    # Catches __init__ args and kwargs before passing them to the superclass, which is object
    def __init__(self, *args, **kwargs):
        logger.debug(f"ComponentBase __init__: {self.__class__.__name__} called with args: {args}, kwargs: {kwargs}")
        super().__init__()

