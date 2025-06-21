"""
Generic Base class for pylium objects.
"""

# Built-in imports
from typing import List, Optional
from datetime import date

# External imports
from pydantic import BaseModel, Field, field_validator



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