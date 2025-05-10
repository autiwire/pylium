from pylium.core.module import Module

from typing import ClassVar, List
import datetime

class Package(Module): 
    """
    A Python package, typically a directory containing an __init__.py file.
    """
    type: ClassVar[Module.Type] = Module.Type.PACKAGE
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=datetime.date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=datetime.date(2025, 5, 10))
    ]
    dependencies: ClassVar[List[Module.Dependency]] = [
        Module.Dependency(name="pydanticX", type=Module.Dependency.Type.PIP, version="2.10.2")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


__all__ = ["Package"]