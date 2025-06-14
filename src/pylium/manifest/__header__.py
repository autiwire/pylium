# Note: This is a special case in the header/impl pattern:
# Usually __impl__.py would import from __header__.py, but here it's reversed because:
# 1. The Manifest class is the core implementation that doesn't know about headers
# 2. The header needs the Manifest class to define its own manifest
# 3. This creates a clean separation where Manifest remains independent of the header concept
# 4. Yet the manifest system still benefits from the recursive structure through __manifest__ and parent resolution
from .__impl__ import Manifest

#print("Hello, World from manifest @ manifest/__header__.py!")

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
    location=Manifest.Location(module=__name__),
    description="Base class for all manifests",    
    status=Manifest.Status.Development,
    aiAccessLevel=Manifest.AIAccessLevel.Read,
    dependencies=[],
    authors=_manifest_core_authors,
    maintainers=_manifest_core_maintainers,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=_manifest_core_authors.rraudzus),
    license=Manifest.licenses.Apache2,
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
        Manifest.Changelog(version="0.1.5", date=Manifest.Date(2025,5,23), author=_manifest_core_authors.rraudzus,
                            notes=["Added doc property to get the docstring of the class or module"]),
        Manifest.Changelog(version="0.1.6", date=Manifest.Date(2025,5,27), author=_manifest_core_authors.rraudzus, 
                            notes=["Added per-module-manifest"]),
        Manifest.Changelog(version="0.1.7", date=Manifest.Date(2025,5,28), author=_manifest_core_authors.rraudzus, 
                            notes=["Moved pylium.core.manifest to pylium.manifest"]),
        Manifest.Changelog(version="0.1.8", date=Manifest.Date(2025,5,28), author=_manifest_core_authors.rraudzus, 
                            notes=["Added ai_access_level to manifest"]),
        Manifest.Changelog(version="0.1.9", date=Manifest.Date(2025,5,28), author=_manifest_core_authors.rraudzus, 
                            notes=["Set manifest ai_access_level to read"]),
        Manifest.Changelog(version="0.1.10", date=Manifest.Date(2025,5,29), author=_manifest_core_authors.rraudzus, 
                            notes=["Added license tag to manifest"]),
        Manifest.Changelog(version="0.1.11", date=Manifest.Date(2025,5,29), author=_manifest_core_authors.rraudzus, 
                            notes=["Set manifest license to Apache2"]),
        Manifest.Changelog(version="0.1.12", date=Manifest.Date(2025,6,13), author=_manifest_core_authors.rraudzus,
                            notes=["Enhanced function manifest support",
                                   "Added @func decorator for attaching manifests to functions",
                                   "Improved manifest location handling for functions",
                                   "Added type detection for module, class, function, and method locations"]),
        Manifest.Changelog(version="0.1.13", date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                            notes=["Moved to header/impl design",
                                   "Added parent property to manifest"]),
        Manifest.Changelog(version="0.1.14", date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                            notes=["Improved manifest parent resolution",
                                   "Added special case for manifest module parent",
                                   "Fixed circular import issues",
                                   "Moved types to _types.py",
                                   "Moved enums to _enums.py",
                                   "Moved license to _license.py",
                                   "Moved flags to _flags.py",
                                   "Created __header__.py from __init__.py contents",
                                   "Reduced __init__.py to minimal interface"]),
        Manifest.Changelog(version="0.1.15", date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                             notes=["Added documentation for function manifest patterns",
                                   "Added examples for both simple and implementation class function manifests"]),
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
        Manifest.Changelog(version="0.1.2", date=Manifest.Date(2025,6,7), author=_manifest_core_authors.rraudzus, 
                          notes=["Added shortName property to manifest class"]),
        Manifest.Changelog(version="0.1.3", date=Manifest.Date(2025,6,14), author=_manifest_core_authors.rraudzus,
                          notes=["Added children property for manifest hierarchy traversal",
                                "Implemented efficient child manifest discovery",
                                "Supports module, class, and function child manifests"])
    ]
)





