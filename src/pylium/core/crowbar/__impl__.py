"""
Implementation of the Crowbar installer and package management system.
"""

from .__header__ import Crowbar, Header
from pylium.manifest import Manifest

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


class CrowbarImpl(Crowbar):
    """
    Implementation of the Crowbar installer and package management system.
    """

    __class_type__ = Header.ClassType.Impl

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    