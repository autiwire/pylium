from pylium.core import __manifest__ as __parent__
from pylium.manifest import Manifest
from pylium.core.header import Header, classProperty, dlock

import threading
from abc import abstractmethod
from typing import Type, Optional, Dict, List

__manifest__ : Manifest = __parent__.createChild(
    location=Manifest.Location(module=__name__, classname=None), 
    description="Installer and package management system for Pylium",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    dependencies=[ Manifest.Dependency(name="pip", version="25.3.0", type=Manifest.DependencyType.PIP, category=Manifest.Dependency.Category.BUILD),
                   Manifest.Dependency(name="setuptools", version="69.0.3", type=Manifest.DependencyType.PIP, category=Manifest.Dependency.Category.BUILD),
                   Manifest.Dependency(name="wheel", version="0.42.0", type=Manifest.DependencyType.PIP, category=Manifest.Dependency.Category.BUILD),
                    ],
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 16), 
                           author=__parent__.authors.rraudzus,
                           notes=["Initial definition of pylium.crowbar package manifest."]),
    ]
)

class Crowbar(Header):
    """
    Installer and package management system for Pylium

    This class provides functionality to:
    - Install and setup the Pylium system
    - Manage packages and dependencies
    - Perform runtime installations
    - Repair and update the system
    """

    __manifest__ : Manifest = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="The Crowbar installer and package management system.",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.CLI,
        dependencies=[],
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,6,16), author=__parent__.authors.rraudzus,
                               notes=["Initial implementation of the Crowbar installer",
                                      "Added basic dependency management",
                                      "Support for pip and system dependencies"]),
            Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,6,20), author=__parent__.authors.rraudzus,
                               notes=["Fixed list_dependencies function routing",
                                      "Improved CLI integration with proper function binding",
                                      "Enhanced stability and reliability of dependency listing"])
        ]
    )

    _default_instance: "Crowbar" = None
    _default_lock = threading.Lock()
 

    @classmethod
    def getDependencies(cls, path: str = "", recursive: bool = True) -> Dict[str, List[Manifest.Dependency]]:
        """
        Get the dependencies of the given object path
        """

        manifest = Manifest.getManifest(path)

        if manifest is None:
            raise ValueError(f"No manifest found for path: {path}")

        dependencies = {}

        if recursive:
            for child in manifest.children:
                dependencies.update(cls.getDependencies(child.location.fqnShort, recursive))

        # Add self to the dependencies if we have elements
        if len(manifest.dependencies) > 0:
            # Root manifest is purely virtual, so it has no location
            if manifest.isRoot:
                dependencies.update({"/": manifest.dependencies})
            else:
                dependencies.update({manifest.location.fqnShort: manifest.dependencies})

        return dependencies

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 


@Manifest.func(__manifest__.createChild(
    location=None,
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 16),
                           author=__parent__.authors.rraudzus,
                           notes=["Added list_dependencies function to list the dependencies of the current package"]),
    ]
))
def list_dependencies(path: str = "", recursive: bool = True):
    """
    List the dependencies of the given object path

    Args:
        path: The path to the object to list the dependencies for
        recursive: If True, list the dependencies of the dependencies
    """

    dependencies = Crowbar.getDependencies(path, recursive)

    print(f"LIST DEPENDENCIES: {path}")
    print(f"  DEPENDENCIES: {dependencies}")
    


@Manifest.func(__manifest__.createChild(
    location=None,
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 16),
                           author=__parent__.authors.rraudzus,
                           notes=["Added list_dependencies function to list the dependencies of the current package"]),
    ]
))
def test_crowbar():
    """
    Test the crowbar
    """
    print("TEST CROWBAR")


@Manifest.func(__manifest__.createChild(
    location=None,
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 16),
                           author=__parent__.authors.rraudzus,
                           notes=["Added test_crowbar2 function to test the crowbar2"]),
    ]
))
def test_crowbar2():
    """
    Test the crowbar2
    """
    print("TEST CROWBAR2")
