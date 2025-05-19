from abc import ABC, abstractmethod, ABCMeta

from typing import ClassVar, List, Optional, Type, Any, Generator, Tuple, Callable, Union
from packaging.version import Version 
import datetime
from enum import Enum
from importlib import import_module
from pathlib import Path
from os.path import join

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
    def __init__(self, tag: str, name: str, email: Optional[str] = None, company: Optional[str] = None, since_version: Optional[str] = None, since_date: Optional[ManifestValue.Date] = None):    
        self.tag = tag
        self.name = name
        self.email = email
        self.company = company
        self.since_version = since_version
        self.since_date = since_date

    def since(self, version: str, date: ManifestValue.Date) -> "ManifestAuthor":
        # return a copy of the author with the since version and date
        return ManifestAuthor(self.tag, self.name, self.email, self.company, version, date)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestAuthor):
            return False
        return self.name == other.name or self.email == other.email
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.name, self.email))
    
    def __str__(self):
        return f"{self.name} ({self.email}) {self.company} {self.since_version} {self.since_date}"

    def __repr__(self):
        return f"{self.name} ({self.email}) {self.company} [since: {self.since_version} @ {self.since_date}]"


class ManifestAuthorList(ManifestValue):
    def __init__(self, authors: List[ManifestAuthor]):
        self._authors = authors

    def __getattr__(self, tag: str) -> ManifestAuthor:        
        for author in self._authors:
            if author.tag == tag:
                return author
        raise AttributeError(f"Author {tag} not found")

    def __getitem__(self, index: int) -> ManifestAuthor:
        return self._authors[index]

    def __len__(self) -> int:
        return len(self._authors)

    def __str__(self):
        return f"{self._authors}"
    
    def __repr__(self):
        return f"{self._authors}"



class ManifestChangelog(ManifestValue):
    def __init__(self, version: Optional[str] = None, date: Optional[ManifestValue.Date] = None, author: Optional[ManifestAuthor] = None, notes: List[str] = []):
        self.version = version
        self.date = date
        self.author = author
        self.notes = notes

    def __str__(self):
        return f"{self.version} ({self.date}) {self.author} {self.notes}"
    
    def __repr__(self):
        return f"{self.version} ({self.date}) {self.author} {self.notes}"


class ManifestCopyright(ManifestValue):
    def __init__(self, date: Optional[ManifestValue.Date], author: Optional[ManifestAuthor] = None):
        self.date = date
        self.author = author

    def __str__(self):
        return f"(c) ({self.date}) {self.author}"
    
    def __repr__(self):
        return f"(c) ({self.date}) {self.author}"
    

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
    # Usually here in header classes the manifest is defined
    __manifest__: ClassVar["Manifest"] = None
    _manifest_core_authors = ManifestAuthorList([
                                        ManifestAuthor(tag="rraudzus", 
                                            name="Rouven Raudzus", 
                                            email="raudzus@autiwire.org", 
                                            company="AutiWire GmbH", 
                                            since_version="0.0.0", 
                                            since_date=datetime.date(2025,5,10))
                                            ])

    Date = ManifestValue.Date
    Location = ManifestLocation
    Author = ManifestAuthor
    AuthorList = ManifestAuthorList
    Changelog = ManifestChangelog
    Dependency = ManifestDependency
    Copyright = ManifestCopyright
    License = ManifestLicense
    Status = ManifestStatus
    

    def __init__(self, 
                location: Location,
                description: str = "",
                changelog: Optional[List[Changelog]] = None, 
                dependencies: Optional[List[Dependency]] = None, 
                authors: Optional[AuthorList] = None,
                copyright: Optional[Copyright] = None,
                license: Optional[License] = None,
                status: Status = Status.Development,
                *args, 
                **kwargs):
        
        self.location: Manifest.Location = location
        self.description: str = description
        self.changelog: List[Manifest.Changelog] = changelog or []
        self.dependencies: List[Manifest.Dependency] = dependencies or []
        self.authors: Manifest.AuthorList = authors or Manifest.AuthorList([])
        self.copyright: Manifest.Copyright = copyright or Manifest.Copyright(date=None, author=None)
        self.license: Manifest.License = license or Manifest.License(name="", url=None)        
        self.status: Manifest.Status = status


    @property
    def contributors(self) -> AuthorList:
        # We create a list of authors from the changelog
        authors = []
        for changelog in self.changelog:
            if changelog.author and changelog.author not in authors:
                authors.append(changelog.author)
        return ManifestAuthorList(authors)


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




# Define Manifests own manifest
Manifest.__manifest__ = Manifest(
    location=Manifest.Location(name=Manifest.__qualname__, module=Manifest.__module__, file=__file__),
    description="Base class for all manifests",    
    status=Manifest.Status.Development,
    dependencies=[Manifest.Dependency(type=Manifest.Dependency.Type.PYLIUM, name="pylium", version="0.1.0")],
    authors=Manifest._manifest_core_authors,
    copyright=Manifest.Copyright(date=Manifest.Date(2025,5,18), author=Manifest._manifest_core_authors.rraudzus),
    license=Manifest.License(name="", url=""),
    changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,5,18), author=Manifest._manifest_core_authors.rraudzus, notes=["Initial release"])],
)

