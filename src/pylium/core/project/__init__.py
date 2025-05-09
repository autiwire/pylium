from pylium.core.package import Package
from pylium.core.module import Module

from typing import ClassVar

class Project(Package):
    """
    A project represented by a directory containing a pyproject.toml file.
    """
    type: ClassVar[Module.Type] = Module.Type.PROJECT
    version: ClassVar[str] = "0.0.3"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

__all__ = ["Project"]