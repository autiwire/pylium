from pylium import __project__
from pylium.manifest import Manifest

__manifest__ = __project__.createChild(
    location=Manifest.Location(module=__name__, classname=None), 
    description="The core functionalities of the Pylium library.",
    status=Manifest.Status.Development,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 5, 28), 
                           author=__project__.authors.rraudzus,
                           notes=["Initial definition of pylium.core package manifest."]),
        Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025, 5, 28), 
                           author=__project__.authors.rraudzus,
                           notes=["Moved manifest definition to __header__.py"])
    ]
)



