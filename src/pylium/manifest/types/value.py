"""
Base value type for the manifest system.
"""

# Pylium imports
from .xobject import XObject

# Standard library imports
import datetime

class ManifestValueTypes:
    """Type definitions for manifest values."""
    Date = datetime.date

class ManifestValue(XObject, ManifestValueTypes):
    """Base class for manifest values with common type definitions."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

