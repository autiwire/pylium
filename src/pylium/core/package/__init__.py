from pylium.core.module import Module

from typing import ClassVar

class Package(Module): 
    """
    A Python package, typically a directory containing an __init__.py file.
    """
    type: ClassVar[Module.Type] = Module.Type.PACKAGE
    version: ClassVar[str] = "0.0.2"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


__all__ = ["Package"]