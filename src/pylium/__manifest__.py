from .core.header.manifest import Manifest

# In __manifest__.py in project source root default values for the manifest are defined
# This is used to ensure that the manifest is always available and can be used to 
# generate the manifest for the project

__manifest__ = Manifest(
    location=Manifest.Location(name=__name__, module=__name__, file=__file__),
    description="Project base manifest",
    status=Manifest.Status.Development,
    dependencies=[Manifest.Dependency(type=Manifest.Dependency.Type.PYLIUM, name="pylium", version="0.1.0")],
    authors=Manifest._manifest_core_authors,
    maintainers=Manifest._manifest_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=Manifest._manifest_core_authors.rraudzus),
    license=Manifest.licenses.NoLicense,
    changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,5,18), author=Manifest._manifest_core_authors.rraudzus, notes=["Initial release"]),
               Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,5,19), author=Manifest._manifest_core_authors.rraudzus, notes=["Added maintainers"]),
               Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,5,20), author=Manifest._manifest_core_authors.rraudzus, notes=["Added license"])],               

)
