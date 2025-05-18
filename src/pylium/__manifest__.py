from .core.header.manifest import Manifest

# In __manifest__.py in project source root default values for the manifest are defined
# This is used to ensure that the manifest is always available and can be used to 
# generate the manifest for the project

Manifest.__manifest__ = Manifest(
    location=Manifest.Location(name=Manifest.__qualname__, module=Manifest.__module__, file=Manifest.__file__),
    description="Base class for all manifests",
    authors=[Manifest.Author(name="Rouven Raudzus", email="raudzus@autiwire.org", company="AutiWire GmbH")],
)
