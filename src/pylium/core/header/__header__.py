from .manifest import Manifest

from abc import ABC, ABCMeta

class HeaderMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        

class Header(ABC, metaclass=HeaderMeta):
    __manifest__: Manifest = Manifest(
        location=Manifest.Location(name=__qualname__, module=__module__, file=__file__),
        description="Base class for all headers",
        authors=[Manifest.Author(name="Rouven Raudzus", email="raudzus@autiwire.org", company="AutiWire GmbH")],
        changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), notes=["Initial release"])],
        dependencies=[Manifest.Dependency(type=Manifest.Dependency.Type.PYLIUM, name="pylium", version="0.1.0")],
        copyright=Manifest.Copyright(name="AutiWire GmbH", date=Manifest.Date(2025,1,1)),
        license=Manifest.License(name="", url=""),
        status=Manifest.Status.Development
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        


