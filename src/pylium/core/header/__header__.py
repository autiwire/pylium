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
        maintainers=__project__.maintainers,
        copyright=__project__.copyright,
        license=__project__.license,
        changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__project__.authors.rraudzus, notes=["Initial release"]),
                   Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=__project__.authors.rraudzus, notes=["Added maintainers pointing to authors of the project"]),
                   Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=__project__.authors.rraudzus, notes=["Added license pointing to project license"])],                           
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        


