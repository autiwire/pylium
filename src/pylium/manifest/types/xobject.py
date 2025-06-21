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
    
    pass