from abc import ABC, abstractmethod, ABCMeta

from typing import ClassVar, List, Optional, Type, Any, Generator, Tuple, Callable, Union
from packaging.version import Version 
import datetime
from enum import Enum

from logging import getLogger
logger = getLogger(__name__)


class ManifestMeta(ABCMeta): # type: ignore
    """
    Metaclass that ensures Manifest instances attached to classes get their location info.
    """
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        # Look for any Manifest instances in class attributes and update their location
        for attr_name, attr_value in dct.items():
            if isinstance(attr_value, Manifest):
                attr_value.set_location_from_class(cls)


class ManifestValue(object):
    Date = datetime.date

    def __init__(self):
        pass


class ManifestLocation(ManifestValue):
    def __init__(self, name: str, module: str, file: str):
        self.name = name
        self.module = module
        self.file = file
        self.fqn = f"{self.module}.{self.name}"

    def __str__(self):
        return f"{self.fqn}"
    
    def __repr__(self):
        return f"{self.fqn} @ {self.file}"


class ManifestDependencyType(Enum):
    PYLIUM = "pylium"
    PIP = "pip"
    APT = "apt"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


class ManifestDependency(ManifestValue):
    Type = ManifestDependencyType
    
    def __init__(self, name: str, version: str, type: Type = Type.PIP):
        self.type = type
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name} ({self.version})"
    
    def __repr__(self):
        return f"{self.name} ({self.version})"


class ManifestAuthor(ManifestValue):
    def __init__(self, name: str, email: Optional[str] = None, company: Optional[str] = None, since_version: Optional[str] = None, since_date: Optional[ManifestValue.Date] = None):    
        self.name = name
        self.email = email
        self.company = company
        self.since_version = since_version
        self.since_date = since_date

    def __str__(self):
        return f"{self.name} ({self.email}) {self.company} {self.since_version} {self.since_date}"
    
    def __repr__(self):
        return f"{self.name} ({self.email}) {self.company} [since: {self.since_version} @ {self.since_date}]"


class ManifestChangelog(ManifestValue):
    def __init__(self, version: Optional[str] = None, notes: List[str] = [], date: Optional[ManifestValue.Date] = None):
        self.version = version
        self.notes = notes
        self.date = date

    def __str__(self):
        return f"{self.version} ({self.date}) {self.notes}"
    
    def __repr__(self):
        return f"{self.version} ({self.date}) {self.notes}"


class ManifestCopyright(ManifestValue):
    def __init__(self, name: str, date: Optional[ManifestValue.Date] = None):
        self.name = name
        self.date = date

    def __str__(self):
        return f"{self.name} ({self.date})"
    
    def __repr__(self):
        return f"{self.name} ({self.date})"
    

class ManifestLicense(ManifestValue):
    def __init__(self, name: str, url: Optional[str] = None):
        self.name = name
        self.url = url
        
    def __str__(self):
        return f"{self.name} ({self.url})"
    
    def __repr__(self):
        return f"{self.name} ({self.url})"
    

class ManifestStatus(Enum):
    Development = "Development"
    Production = "Production"
    Deprecated = "Deprecated"
    Archived = "Archived"
    Unstable = "Unstable"
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value

class Manifest:
    """
    Metadata about a code unit (module, class, etc.).
    Can optionally include location information.
    
    Metadata includes:
    - Description and documentation
    - Version information and changelog
    - Authors and maintainers
    - Dependencies
    - License and copyright information
    - Optional: Location information (name, module, file, fqn)
    """

    # Manifests own manifest
    __manifest__: ClassVar["Manifest"] = None
    
    # Get the default manifest.
    @classmethod
    def __default_manifest__(cls) -> "Manifest":
        # the default manifest is the one defined in a project's __manifest__.py file
        from importlib import import_module
        from pathlib import Path
        from os.path import join

        # walk module path upwards until __manifest__.py is found
        # don't leave package root
        module_path = cls.__module__
        while module_path:
            manifest_path = join(module_path, "__manifest__.py")
            if Path(manifest_path).exists():
                break
            module_path = module_path.rsplit(".", 1)[0]

        if not module_path:
            raise ValueError("No __manifest__.py file found")

        module = import_module(module_path)
        return module.__manifest__


    Date = ManifestValue.Date
    Location = ManifestLocation
    Author = ManifestAuthor
    Changelog = ManifestChangelog
    Dependency = ManifestDependency
    Copyright = ManifestCopyright
    License = ManifestLicense
    Status = ManifestStatus
    
    def __init__(self, 
                location: Location,
                description: str = "",
                authors: Optional[List[Author]] = None, 
                changelog: Optional[List[Changelog]] = None, 
                dependencies: Optional[List[Dependency]] = None, 
                copyright: Optional[Copyright] = None,
                license: Optional[License] = None,
                status: Status = Status.Development,
                *args, 
                **kwargs):
        
        self.location: Manifest.Location = location
        self.description: str = description
        self.authors: List[Manifest.Author] = authors or []
        self.changelog: List[Manifest.Changelog] = changelog or []
        self.dependencies: List[Manifest.Dependency] = dependencies or []
        self.copyright: Manifest.Copyright = copyright or Manifest.Copyright(name="", date=None)
        self.license: Manifest.License = license or Manifest.License(name="", url=None)        
        self.status: Manifest.Status = status


    @property
    def version(self) -> Version:
        # Determine the version: latest changelog entry, or 0.0.0
        if self.changelog:
            return Version(self.changelog[-1].version) if self.changelog[-1].version else Version("0.0.0")
        return Version("0.0.0")

    @property
    def author(self) -> str:
        if self.authors:
            return self.authors[0].name
        return ""

    @property
    def maintainer(self) -> str:
        if self.authors:
            return self.authors[0].name
        return ""

    @property
    def email(self) -> str:
        if self.authors:
            return self.authors[0].email or ""
        return ""

    @property
    def credits(self) -> List[str]:
        return [author.name for author in self.authors]

    def __str__(self):
        base = f"Manifest (version={self.version}, author={self.author}, status={self.status}, dependencies={len(self.dependencies)})"
        return f"{base} @ {self.location}"

    def __repr__(self):
        base = f"Manifest (version={self.version}, author={self.author}, status={self.status}, dependencies={len(self.dependencies)})"
        return f"{base} @ {repr(self.location)}"

    def __hash__(self):
        return hash((self.version, self.author, self.status, 
                    self.location.name, self.location.module, 
                    self.location.file, self.location.fqn))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return False
        return (self.version == other.version and 
                self.author == other.author and 
                self.status == other.status and
                self.location.name == other.location.name and
                self.location.module == other.location.module and
                self.location.file == other.location.file and
                self.location.fqn == other.location.fqn)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Manifest):
            return self.version < other.version
        return False

    def __le__(self, other: Any) -> bool:
        if isinstance(other, Manifest):
            return self.version <= other.version
        return False

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Manifest):
            return self.version > other.version
        return False

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, Manifest):
            return self.version >= other.version
        
Manifest.__manifest__ = Manifest(
    location=Manifest.Location(name=Manifest.__qualname__, module=Manifest.__module__, file=__file__),
    description="Base class for all manifests",
    authors=[Manifest.Author(name="Rouven Raudzus", email="raudzus@autiwire.org", company="AutiWire GmbH")],
    changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,5,18), notes=["Initial release"])],
    dependencies=[Manifest.Dependency(type=Manifest.Dependency.Type.PYLIUM, name="pylium", version="0.1.0")],
    copyright=Manifest.Copyright(name="AutiWire GmbH", date=Manifest.Date(2025,5,18)),
    license=Manifest.License(name="", url=""),
    status=Manifest.Status.Development
)

