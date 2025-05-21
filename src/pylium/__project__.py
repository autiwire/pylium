from .core.manifest import Manifest, _manifest_core_authors, _manifest_core_maintainers

# In __manifest__.py in project source root default values for the manifest are defined.
# This is used to ensure that the manifest is always available and can be used to 
# generate the manifests for modules and classes in the project.
# Simply do so by creating a child manifest in the module or class with createChild() method.
# You don't need to import _manifest_core_* variables, create your own private variables instead.
# For an example look at the pylium.core.header.Header class.

__manifest__ = Manifest(
    location=Manifest.Location(module=__name__),
    description="Pylium project",
    status=Manifest.Status.Development,
    dependencies=[],
    authors=_manifest_core_authors,
    maintainers=_manifest_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus),
    license=Manifest.licenses.NoLicense,
    changelog=[ Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus, 
                                    notes=["Initial release"]),
                Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=_manifest_core_authors.rraudzus, 
                                    notes=["Added maintainers"]),
                Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=_manifest_core_authors.rraudzus, 
                                    notes=["Added license"]),
                Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,5,21), author=_manifest_core_authors.rraudzus, 
                                    notes=["Renamed file to __project__.py"])
                ],
)

__all__ = ["__manifest__", "Manifest"]