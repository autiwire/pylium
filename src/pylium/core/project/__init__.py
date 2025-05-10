from pylium.core.package import Package
from pylium.core.module import Module

from typing import ClassVar, List
import datetime

class Project(Package):
    """
    A project represented by a directory containing a pyproject.toml file.
    """
    type: ClassVar[Module.Type] = Module.Type.PROJECT
    version: ClassVar[str] = "0.0.1"
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=datetime.date(2025, 5, 10))
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

__all__ = ["Project"]