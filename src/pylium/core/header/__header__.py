from .manifest import Manifest
from pylium import __project__

from abc import ABC, ABCMeta

class HeaderMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        

class Header(ABC, metaclass=HeaderMeta):
    Manifest = Manifest
    
    __manifest__: Manifest = Manifest(
        location=Manifest.Location(name=__qualname__, module=__module__, file=__file__),
        description="Base class for all headers",
        status=Manifest.Status.Development,
        dependencies=[],
        authors=__project__.__manifest__.authors,
        maintainers=__project__.__manifest__.maintainers,
        copyright=__project__.__manifest__.copyright,
        license=__project__.__manifest__.license,
        changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__project__.__manifest__.authors.rraudzus, notes=["Initial release"]),
                   Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=__project__.__manifest__.authors.rraudzus, notes=["Added maintainers pointing to authors of the project"]),
                   Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=__project__.__manifest__.authors.rraudzus, notes=["Added license pointing to project license"])],                           
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        


