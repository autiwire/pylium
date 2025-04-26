from ._component import _PackageHeaderComponent

from typing import ClassVar, Optional, Dict, List

class _PackageHeader(_PackageHeaderComponent):
    """
    This is the base class for all Pylium header components.
    """

    # *** subclass overrides ***

    # The name of the component - used to register the component (set once per inheritance hierarchy)
    __component__ = "header"

    # Components dependencies (pip packages) (set per-package)
    __dependencies__: List[str] = ["sqlmodel", "pydantic", "sqlalchemy"]

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    # *** class methods ***
    def __new__(cls, *args, **kwargs):
        print(f"Header new: {cls.__module__}")
        from ._impl import _PackageImplMixin
        # Get the implementation class
        impl_cls = cls.get_sibling_component(_PackageImplMixin)
        if impl_cls is not None:
            print(f"Impl class: {impl_cls.__name__}")
            # Create instance of implementation class
            return object.__new__(impl_cls)
        else:
            print("No impl class found")
            # Create instance of current class
            return object.__new__(cls)

    def __init__(self):
        print(f"Header init: {self.__module__}")
        super().__init__()

_PackageHeader.register()
