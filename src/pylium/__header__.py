try:
    from ._version import version as __version__
except ImportError:
    # This is a fallback for cases where the package is not installed
    # or _version.py has not been generated (e.g., a raw source checkout).
    __version__ = "0.0.0.unknown" # Or some other placeholder

#print("Hello, World from pylium/__header__.py!")

from .manifest import Manifest


_project_core_authors = Manifest.AuthorList.create([
    Manifest.__manifest__.authors.rraudzus,
])

_project_core_maintainers = Manifest.AuthorList.create(_project_core_authors.authors.copy())

__manifest__ : Manifest = Manifest.__root_manifest__.createChild(
    location=Manifest.Location(module=__name__),
    description="Pylium project",
    status=Manifest.Status.Development,
    dependencies=[],
    authors=_project_core_authors,
    maintainers=_project_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=_project_core_authors.rraudzus),
    license=Manifest.Licenses.NoLicense,
    frontend=Manifest.Frontend.CLI,
    changelog=[ Manifest.Changelog(version=Manifest.Version("0.1.0"), date=Manifest.Date(2025,5,18), author=_project_core_authors.rraudzus, 
                                    notes=["Initial release"]),
                Manifest.Changelog(version=Manifest.Version("0.1.1"), date=Manifest.Date(2025,5,19), author=_project_core_authors.rraudzus, 
                                    notes=["Added maintainers"]),
                Manifest.Changelog(version=Manifest.Version("0.1.2"), date=Manifest.Date(2025,5,20), author=_project_core_authors.rraudzus, 
                                    notes=["Added license"]),
                Manifest.Changelog(version=Manifest.Version("0.1.3"), date=Manifest.Date(2025,5,21), author=_project_core_authors.rraudzus, 
                                    notes=["Renamed file to __project_manifest__.py"]),
                Manifest.Changelog(version=Manifest.Version("0.1.4"), date=Manifest.Date(2025,5,28), author=_project_core_authors.rraudzus, 
                                    notes=["Removed __project_manifest__.py, instead use __project_manifest__ = __manifest__ to define the project manifest"]),
                Manifest.Changelog(version=Manifest.Version("0.1.5"), date=Manifest.Date(2025,5,28), author=_project_core_authors.rraudzus, 
                                    notes=["Added __version__"]),
                Manifest.Changelog(version=Manifest.Version("0.1.6"), date=Manifest.Date(2025,5,28), author=_project_core_authors.rraudzus, 
                                    notes=["Moved __version__, __manifest__ and __project_manifest__ to __header__.py"]),
                Manifest.Changelog(version=Manifest.Version("0.2.0"), date=Manifest.Date(2025,6,8), author=_project_core_authors.rraudzus,
                                    notes=["Major CLI system overhaul with tree-based architecture",
                                           "Added recursive navigation and multi-frontend support foundation"]),
                ],
)

# This manifest is defined as a project manifest. By doing this, this module will become the project root.
__project_manifest__ = __manifest__

