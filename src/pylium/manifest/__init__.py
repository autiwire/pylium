from ._manifest import Manifest

print("Hello, World from manifest @ manifest/__init__.py!")

# Core authors for use in own manifest
_manifest_core_authors = Manifest.AuthorList([
    Manifest.Author(tag="rraudzus", 
        name="Rouven Raudzus", 
        email="raudzus@autiwire.org", 
        company="AutiWire GmbH", 
        since_version="0.0.0", 
        since_date=Manifest.Date(2025,5,10))
        ])    


# Core maintainers, initially same as authors
_manifest_core_maintainers = Manifest.AuthorList(_manifest_core_authors._authors.copy())

# Define Manifests own manifest (per-module-manifest)
__manifest__ = Manifest(
    location=Manifest.Location(module=__name__, classname=Manifest.__qualname__),
    description="Base class for all manifests",    
    status=Manifest.Status.Development,
    dependencies=[],
    authors=_manifest_core_authors,
    maintainers=_manifest_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus),
    license=Manifest.licenses.NoLicense,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus, 
                            notes=["Initial release"]),
        Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=_manifest_core_authors.rraudzus, 
                            notes=["Added maintainers"]),
        Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=_manifest_core_authors.rraudzus, 
                            notes=["Added license"]),
        Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,5,21), author=_manifest_core_authors.rraudzus, 
                            notes=["Modified location information, requires less parameters"]),
        Manifest.Changelog(version="0.1.4", date=Manifest.Date(2025,5,22), author=_manifest_core_authors.rraudzus, 
                            notes=["Moved _manifest_core_* from class to module for more compactness"]),
        Manifest.Changelog(version="0.1.5", date=Manifest,
                            notes=["Added doc property to get the docstring of the class or module"]),
        Manifest.Changelog(version="0.1.6", date=Manifest.Date(2025,5,27), author=_manifest_core_authors.rraudzus, 
                            notes=["Added per-module-manifest"]),
        Manifest.Changelog(version="0.1.7", date=Manifest.Date(2025,5,28), author=_manifest_core_authors.rraudzus, 
                            notes=["Moved pylium.core.manifest to pylium.manifest"]),
    ]
)

# Define Manifests own manifest (per-class-manifest)
Manifest.__manifest__ = __manifest__.createChild(
    location=Manifest.Location(module=__name__, classname=Manifest.__qualname__),
    description="Base class for all manifests",    
    status=Manifest.Status.Development,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus, 
                            notes=["Initial release"]),
        Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=_manifest_core_authors.rraudzus, 
                            notes=["Added per-class-manifest"]),
    ]
)

__all__ = ["__manifest__", "Manifest"]

