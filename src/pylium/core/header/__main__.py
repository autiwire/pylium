from . import Header 
from .manifest import Manifest
from pylium import __project__

print(__project__.__manifest__)
print(Manifest.__manifest__)

h = Header()

print(h.__manifest__)

class X(Header):
    """
    This is a test class.
    """
    __manifest__ = Manifest(
        location=Manifest.Location(module=__module__, classname=__qualname__),
        description="Test class",
        status=Manifest.Status.Development,
        dependencies=[],
        authors=__project__.__manifest__.authors,
        maintainers=__project__.__manifest__.maintainers,
        copyright=__project__.__manifest__.copyright,
        license=__project__.__manifest__.license,
        changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__project__.__manifest__.authors.rraudzus, notes=["Initial release"])],
    )

print(X.__manifest__)

print(X.__manifest__.doc)