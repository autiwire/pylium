"""
Generic Base class for pylium objects.
"""

# External imports
from pydantic import BaseModel


class XObject(BaseModel):
    """
    Generic base class for pylium objects.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.model_dump_json(indent=2)
    
    def __repr__(self):
        return self.model_dump_json(indent=2)