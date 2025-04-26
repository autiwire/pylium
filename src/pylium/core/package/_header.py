from ._component import _PackageComponent

from typing import ClassVar, Optional, Dict
from sqlalchemy import MetaData

class _PackageHeader(_PackageComponent):
    """
    This is the base class for all Pylium header components.
    """

    # *** subclass overrides ***

    # Abstract class - determines if this can be initialized (per-class)
    __abstract__ = True

    # The name of the component - used to register the component (set once per inheritance hierarchy)
    __component__ = "header"

    # *** class methods ***
    def __new__(cls, *args, **kwargs):
        print(f"Header new: {cls.__module__}")
        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        print(f"Header init: {self.__module__}")
        super().__init__()

_PackageHeader.register()
