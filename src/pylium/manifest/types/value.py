"""
Base class for all manifest values.
"""

# Pylium imports
from .xobject import XObject

# Built-in imports
from typing import ClassVar
import datetime


class ManifestValue(object):
    """Base marker class for various manifest data structures."""
    Date: ClassVar[type] = datetime.date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)