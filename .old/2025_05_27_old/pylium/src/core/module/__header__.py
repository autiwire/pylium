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

from pylium import __project__
from pylium.core.header import Header

class Module2(Header):
    """
    A module represented by a set of python files.

    - project/package/module.py - Bundle + Public Interface
    - project/package/module_h.py - Header (optional)
    - project/package/module_impl.py - Implementation (optional)

    """
    
    __manifest__ = Header.Manifest(
        location=Header.Manifest.Location(module=__name__, classname=__qualname__),
        description="Module2",
        status=Header.Manifest.Status.Development,
        dependencies=[],
        authors=__project__.__manifest__.authors,
        maintainers=__project__.__manifest__.maintainers,
        copyright=__project__.__manifest__.copyright,
        license=__project__.__manifest__.license,
        changelog=[],
    )
    
    type: ClassVar[_ModuleBase.Type] = _ModuleBase.Type.MODULE



