from typing import List, ClassVar, Optional, Any, Callable
from enum import Enum
from abc import ABC, abstractmethod, ABCMeta
import dataclasses
import os
import sys
import datetime

import logging
logger = logging.getLogger(__name__)

from ._base import _ModuleBase

class Module(_ModuleBase):
    """
    A module represented by a single Python (.py) file.
    """
    type: ClassVar[_ModuleBase.Type] = _ModuleBase.Type.MODULE
    authors: ClassVar[List[_ModuleBase.AuthorInfo]] = [
        _ModuleBase.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=datetime.date(2025, 5, 10))
    ]
    changelog: ClassVar[List[_ModuleBase.ChangelogEntry]] = [
        _ModuleBase.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=datetime.date(2025, 5, 10))
    ]
    dependencies: ClassVar[List[_ModuleBase.Dependency]] = [
        _ModuleBase.Dependency(name="pydantic", type=_ModuleBase.Dependency.Type.PIP, version="2.10.2"),
        _ModuleBase.Dependency(name="fire", type=_ModuleBase.Dependency.Type.PIP, version="0.5.0"),
    ]

    @classmethod
    def cli(cls, *args, **kwargs):
        """
        Entry point for CLI interface. Here we start the App with the CLI mode and the current module as the CLI entry.
        """

        from pylium.core.app import App
        app = App()
        app.run(App.RunMode.CLI, cls)

__all__ = ["Module"]