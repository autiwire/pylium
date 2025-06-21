from .manifest.__impl__ import Manifest
from .manifest.types import ManifestTypes as Types
from .manifest.types.location import ManifestLocation

print("Hello, World!")

print(Manifest)
print(Manifest.__manifest__)

# Create a test location
location = ManifestLocation(
    module="pylium.manifest.__header__",
    classname="Manifest"
)

# Print the computed fields
print("Computed fields:")
print(f"file: {location.file}")
print(f"fqn: {location.fqn}")
print(f"fqnShort: {location.fqnShort}")
print(f"shortName: {location.shortName}")
print(f"localName: {location.localName}")
print(f"isPackage: {location.isPackage}")
print(f"isModule: {location.isModule}")
print(f"isClass: {location.isClass}")
print(f"isFunction: {location.isFunction}")
print(f"isMethod: {location.isMethod}")

# Print the JSON representation
print("\nJSON dump:")
print(location.model_dump_json(indent=2))