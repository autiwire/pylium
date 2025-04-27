from ._component import Component
from ._header import Header
from ._impl import Impl

from typing import ClassVar

class Package(Header):
    
    Component: ClassVar = Component
    Impl: ClassVar = Impl

    def __init__(self, *args, **kwargs):
        print("Package __init__")
        super().__init__(*args, **kwargs)
       
    def __new__(cls, *args, **kwargs):
        print("Package __new__")
        return super().__new__(cls, *args, **kwargs)

__all__ = ["Package"]
