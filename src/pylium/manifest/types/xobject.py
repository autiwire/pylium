"""
Generic Base class for pylium objects.
"""

# Standard imports
from enum import Enum

# External imports
from pydantic import BaseModel

class XObjectStyle(str, Enum):
    """
    Style of the object
    """
    NONE = "none"
    TREE = "tree"
    TABLE = "table"
    LINEAR = "linear"


class XObjectTypes():
    """
    Types for XObject
    """
    Style = XObjectStyle


class XObject(BaseModel, XObjectTypes):
    """
    Generic base class for pylium objects.
    """
    
    __style__: XObjectStyle = XObjectStyle.NONE

    def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        super().__init__(**kwargs)

    def __str__(self):
        return self.model_dump_json(indent=2)
    
    def __repr__(self):
        return self.model_dump_json(indent=2)
    
    