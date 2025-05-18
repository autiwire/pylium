from ._base import _ModuleBase

from typing import List, ClassVar

class Module(_ModuleBase):
    """
    A module represented by a set of python files.

    - project/package/module.py - Bundle + Public Interface
    - project/package/module.h.py - Header (optional)
    - project/package/module.impl.py - Implementation (optional)
    """
    type: ClassVar[_ModuleBase.Type] = _ModuleBase.Type.MODULE
    authors: ClassVar[List[_ModuleBase.AuthorInfo]] = [
        _ModuleBase.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=_ModuleBase.Date(2025, 5, 10))
    ]
    changelog: ClassVar[List[_ModuleBase.ChangelogEntry]] = [
        _ModuleBase.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=_ModuleBase.Date(2025, 5, 10))
    ]
    dependencies: ClassVar[List[_ModuleBase.Dependency]] = [
        _ModuleBase.Dependency(name="pydantic", type=_ModuleBase.Dependency.Type.PIP, version="2.10.2"),
    ]