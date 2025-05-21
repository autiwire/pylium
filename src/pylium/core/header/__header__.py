from abc import ABC, ABCMeta
from pylium import __project__
from pylium.core.manifest import Manifest

class HeaderMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        

class Header(ABC, metaclass=HeaderMeta):
    Manifest = Manifest
    
    __manifest__: Manifest = __project__.__manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="Base class for all headers",
        status=Manifest.Status.Development,
        dependencies=[],
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Initial release"]),
            Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Added maintainers pointing to authors of the project"]),
            Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Added license pointing to project license"]),
            Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,5,21), author=__project__.__manifest__.authors.rraudzus, 
                                 notes=["Creating manifest as child of project manifest now"])
        ]
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        


