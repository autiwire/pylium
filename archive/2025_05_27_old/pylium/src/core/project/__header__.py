from pylium.core.package import Package
from pylium.core.module import Module

from typing import ClassVar, List

class Project(Package):
    """
    A project represented by a directory containing a pyproject.toml file.

    - project/pyproject.toml - Project definition
    - project/setup.py - Automated installer using pylium deps and install system
    - project/package/__init__.py - Bundle + Public Interface
    - project/package/__header__.py - Header (optional)
    - project/package/__impl__.py - Implementation (optional)
    """
    type: ClassVar[Module.Type] = Module.Type.PROJECT
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version=Manifest.Version("0.0.1"), since_date=Module.Date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version=Manifest.Version("0.0.1"), notes=["Initial release"], date=Module.Date(2025, 5, 10))
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

__all__ = ["Project"]