"""




"""

from ._meta import _PyliumMeta

from abc import ABC

class _Pylium(ABC, metaclass=_PyliumMeta):
    """
    This is the base class for all Pylium components.
    """

    Meta = _PyliumMeta

    def test(self):
        
        print("test")

    