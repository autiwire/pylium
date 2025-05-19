from .manifest import Manifest
from pylium.__manifest__ import __manifest__ as __project__

from abc import ABC, ABCMeta

class HeaderMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        

class Header(ABC, metaclass=HeaderMeta):
    __manifest__: Manifest = Manifest(
        location=Manifest.Location(name=__qualname__, module=__module__, file=__file__),
        description="Base class for all headers",
        status=Manifest.Status.Development,
        dependencies=[Manifest.Dependency(type=Manifest.Dependency.Type.PYLIUM, name="pylium", version="0.1.0")],
        authors=__project__.authors,
        copyright=Manifest.Copyright(date=Manifest.Date(2025,1,1), author=__project__.authors.rraudzus),
        license=Manifest.License(name="", url=""),
        changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__project__.authors.rraudzus, notes=["Initial release"])],
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        


