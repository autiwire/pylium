try:
    from ._version import version as __version__
except ImportError:
    # This is a fallback for cases where the package is not installed
    # or _version.py has not been generated (e.g., a raw source checkout).
    __version__ = "0.0.0.unknown" # Or some other placeholder

print("Hello, World from pylium/__init__.py!")

from .manifest import Manifest

_project_core_authors = Manifest.AuthorList([
    Manifest.__manifest__.authors.rraudzus,
])

_project_core_maintainers = Manifest.AuthorList(_project_core_authors._authors.copy())

__manifest__ = Manifest(
    location=Manifest.Location(module=__name__),
    description="Pylium project",
    status=Manifest.Status.Development,
    dependencies=[],
    authors=_project_core_authors,
    maintainers=_project_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=_project_core_authors.rraudzus),
    license=Manifest.licenses.NoLicense,
    changelog=[ Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,5,18), author=_project_core_authors.rraudzus, 
                                    notes=["Initial release"]),
                Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=_project_core_authors.rraudzus, 
                                    notes=["Added maintainers"]),
                Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=_project_core_authors.rraudzus, 
                                    notes=["Added license"]),
                Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,5,21), author=_project_core_authors.rraudzus, 
                                    notes=["Renamed file to __project__.py"]),
                Manifest.Changelog(version="0.1.4", date=Manifest.Date(2025,5,28), author=_project_core_authors.rraudzus, 
                                    notes=["Removed __project__.py, instead use __project__ = __manifest__ to define the project manifest"]),
                ],
)

# This manifest is defined as a project manifest. By doing this, this module will become the project root.
__project__ = __manifest__

__all__ = ["__project__", "__manifest__"]
