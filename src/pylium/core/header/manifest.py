from abc import ABC, abstractmethod, ABCMeta

from typing import ClassVar, List, Optional, Type, Any, Generator, Tuple, Callable, Union
from packaging.version import Version 

import datetime
import inspect
from enum import Enum
import importlib.machinery
import importlib.util
from pathlib import Path
from os.path import join
import sys
from types import ModuleType
import inspect

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
    def __init__(self, module: str, classname: Optional[str] = None):
        """
        Create a manifest location.
        
        Args:
            module: The module name:
                   - For modules: use __name__
                   - For classes: use __module__
            classname: Optional class name (typically __qualname__ for classes)
        """
        self.module = module
        self.classname = classname
        
        # Get the file location from the module name
        spec = importlib.util.find_spec(self.module)
        if spec is None or spec.origin is None:
            raise ImportError(f"Could not find module {self.module}")
            
        self.file = str(Path(spec.origin).resolve())
        self.fqn = f"{self.module}.{self.classname}" if self.classname else self.module

    def __str__(self):
        return f"{self.fqn}"
    
    def __repr__(self):
        return f"{self.fqn} @ {self.file}"


class ManifestDependencyType(Enum):
    PYLIUM = "pylium"
    PIP = "pip"

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
        return self.tag == other.tag
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.tag))
    
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
    
    def __iter__(self) -> Generator[ManifestAuthor, None, None]:
        return iter(self._authors)


# After ManifestAuthorList definition but before Manifest class
# Type alias for maintainers list - semantically different but technically the same
ManifestMaintainerList = ManifestAuthorList
ManifestContributorsList = ManifestAuthorList


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
    def __init__(self, spdx: str, name: str, url: Optional[str] = None):
        self.spdx = spdx
        self.name = name
        self.url = url

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ManifestLicense):
            return False
        return self.spdx == other.spdx
    
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __str__(self):
        return f"{self.spdx} ({self.name}) {self.url}"
    
    def __repr__(self):
        return f"{self.spdx} ({self.name}) {self.url}"
    

class ManifestLicenseList(ManifestValue):
    def __init__(self, licenses: List[ManifestLicense]):
        self._licenses = licenses

    def __getattr__(self, spdx: str) -> ManifestLicense:        
        for license in self._licenses:
            if license.spdx == spdx:
                return license
        raise AttributeError(f"License {spdx} not found")

    def __str__(self):
        return f"{self._licenses}"
    
    def __repr__(self):
        return f"{self._licenses}"
    
    def __getitem__(self, index: int) -> ManifestLicense:
        return self._licenses[index]
    
    def __len__(self) -> int:
        return len(self._licenses)
    
    def __iter__(self) -> Generator[ManifestLicense, None, None]:
        return iter(self._licenses)
        

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
    
    Manifests can be hierarchical:
    - Project manifest: Root manifest in __init__.py
    - Module manifest: One per module, inherits from project
    - Class manifest: Optional, for classes needing specific metadata
    
    Child manifests can be created using:
    manifest.createChild(location="new location") or
    Manifest.from_parent(parent_manifest, location="new location")
    """

    # Manifests own manifest
    # Usually here in header classes the manifest is defined
    __manifest__: ClassVar["Manifest"] = None

    Date = ManifestValue.Date
    Location = ManifestLocation
    Author = ManifestAuthor
    AuthorList = ManifestAuthorList
    MaintainerList = ManifestMaintainerList
    ContributorsList = ManifestContributorsList
    Changelog = ManifestChangelog
    Dependency = ManifestDependency
    Copyright = ManifestCopyright
    License = ManifestLicense
    Status = ManifestStatus

    # Default licenses to pick from
    licenses = ManifestLicenseList([
        ManifestLicense("NoLicense", "No license", None),
        ManifestLicense("MIT", "MIT License", "https://opensource.org/licenses/MIT"),
        ManifestLicense("Apache-2.0", "Apache License 2.0", "https://opensource.org/licenses/Apache-2.0"),
        ManifestLicense("GPL-2.0", "GNU General Public License v2.0", "https://opensource.org/licenses/GPL-2.0"),
        ManifestLicense("GPL-3.0", "GNU General Public License v3.0", "https://opensource.org/licenses/GPL-3.0"),
        ManifestLicense("LGPL-2.0", "GNU Lesser General Public License v2.0", "https://opensource.org/licenses/LGPL-2.0"),
        ManifestLicense("LGPL-2.1", "GNU Lesser General Public License v2.1", "https://opensource.org/licenses/LGPL-2.1"),
        ManifestLicense("LGPL-3.0", "GNU Lesser General Public License v3.0", "https://opensource.org/licenses/LGPL-3.0"),
        ManifestLicense("BSD-2-Clause", "BSD 2-Clause \"Simplified\" License", "https://opensource.org/licenses/BSD-2-Clause"),
        ManifestLicense("BSD-3-Clause", "BSD 3-Clause \"New\" or \"Revised\" License", "https://opensource.org/licenses/BSD-3-Clause"),
        ManifestLicense("BSD-4-Clause", "BSD 4-Clause \"Original\" or \"Old\" License", "https://opensource.org/licenses/BSD-4-Clause"),
        ManifestLicense("Zlib", "Zlib License", "https://opensource.org/licenses/Zlib"),
        ManifestLicense("BSL-1.0", "Boost Software License 1.0", "https://opensource.org/licenses/BSL-1.0"),
        ManifestLicense("Artistic-2.0", "Artistic License 2.0", "https://opensource.org/licenses/Artistic-2.0"),
        ManifestLicense("MPL-1.1", "Mozilla Public License 1.1", "https://opensource.org/licenses/MPL-1.1"),
        ManifestLicense("MPL-2.0", "Mozilla Public License 2.0", "https://opensource.org/licenses/MPL-2.0"),
        ManifestLicense("EPL-1.0", "Eclipse Public License 1.0", "https://opensource.org/licenses/EPL-1.0"),
        ManifestLicense("EPL-2.0", "Eclipse Public License 2.0", "https://opensource.org/licenses/EPL-2.0"),
        ManifestLicense("AGPL-3.0", "GNU Affero General Public License v3.0", "https://opensource.org/licenses/AGPL-3.0"),
        ManifestLicense("CDDL-1.0", "Common Development and Distribution License 1.0", "https://opensource.org/licenses/CDDL-1.0"),
        ManifestLicense("CC0-1.0", "Creative Commons Zero v1.0 Universal", "https://creativecommons.org/publicdomain/zero/1.0/"),
        ManifestLicense("CC-BY-4.0", "Creative Commons Attribution 4.0", "https://creativecommons.org/licenses/by/4.0/"),
        ManifestLicense("Python-2.0", "Python Software Foundation License 2.0", "https://opensource.org/licenses/Python-2.0"),
        ManifestLicense("OFL-1.1", "SIL Open Font License 1.1", "https://opensource.org/licenses/OFL-1.1"),
        ManifestLicense("Unlicense", "The Unlicense", "https://unlicense.org/"),
    ])


    def __init__(self, 
                location: Location,
                description: str = "",
                changelog: Optional[List[Changelog]] = None, 
                dependencies: Optional[List[Dependency]] = None, 
                authors: Optional[AuthorList] = None,
                maintainers: Optional[MaintainerList] = None,
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
        # Maintainers defaults to authors if not specified, but as a new list
        self.maintainers: Manifest.MaintainerList = maintainers or Manifest.MaintainerList(self.authors._authors.copy() if authors else [])
        self.copyright: Manifest.Copyright = copyright or Manifest.Copyright(date=None, author=None)
        self.license: Manifest.License = license or Manifest.License(name="", url=None)        
        self.status: Manifest.Status = status


    @property
    def contributors(self) -> ContributorsList:
        # We create a list of contributors from authors, maintainers, and changelog entries
        contributors = []
        
        # Add original authors first
        for author in self.authors:
            if author not in contributors:
                contributors.append(author)
        
        # Add maintainers
        for maintainer in self.maintainers:
            if maintainer not in contributors:
                contributors.append(maintainer)
                
        # Add changelog authors
        for changelog in self.changelog:
            if changelog.author and changelog.author not in contributors:
                contributors.append(changelog.author)
                
        return Manifest.ContributorsList(contributors)


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
        if self.maintainers:
            return self.maintainers[0].name
        return ""

    @property
    def email(self) -> str:
        if self.authors:
            return self.authors[0].email or ""
        return ""

    @property
    def credits(self) -> List[str]:
        return [author.name for author in self.authors]

    @property
    def created(self) -> Date:
        if self.changelog:
            return self.changelog[0].date
        return None

    @property
    def updated(self) -> Date:
        if self.changelog:
            return self.changelog[-1].date
        return None

    @property
    def doc(self) -> str:
        if self.location.classname:
            # get the docstring from the class "classname" in module "module"
            # therefor import the module and get the class. check that its in the class itself and not in a parent class
            module = importlib.import_module(self.location.module)
            cls = getattr(module, self.location.classname)
            if cls.__doc__:
                return cls.__doc__.strip()
            else:
                return ""
        else:
            # get the docstring from the module
            module = importlib.import_module(self.location.module)
            return inspect.getdoc(module).strip()

    def __str__(self):
        base = f"Manifest (version={self.version}, author={self.author}, status={self.status}, dependencies={len(self.dependencies)})"
        return f"{base} @ {self.location}"

    def __repr__(self):
        base = f"Manifest (version={self.version}, author={self.author}, status={self.status}, dependencies={len(self.dependencies)})"
        return f"{base} @ {repr(self.location)}"

    def __hash__(self):
        return hash((self.version, self.author, self.status, 
                    self.location.classname, self.location.module, 
                    self.location.file, self.location.fqn))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return False
        return (self.version == other.version and 
                self.author == other.author and 
                self.status == other.status and
                self.location.classname == other.location.classname and
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

    def createChild(self, 
                   location: Location,
                   description: Optional[str] = None,
                   changelog: Optional[List[Changelog]] = None,
                   dependencies: Optional[List[Dependency]] = None,
                   authors: Optional[AuthorList] = None,
                   maintainers: Optional[MaintainerList] = None,
                   copyright: Optional[Copyright] = None,
                   license: Optional[License] = None,
                   status: Optional[Status] = None) -> "Manifest":
        """
        Create a child manifest inheriting from this manifest.
        Only specified fields will override the parent's values.
        
        Dependencies are NOT inherited from parent as they follow module hierarchy
        rather than manifest hierarchy. Each module should explicitly declare its
        own dependencies based on what it actually uses.
        
        Example:
            project_manifest.createChild(
                location=Location(...),
                description="Module-specific description",
                dependencies=[Dependency(...)]  # Module's own dependencies
            )
        """
        return self.__class__(
            location=location,
            description=description or self.description,
            changelog=changelog or self.changelog.copy(),
            dependencies=dependencies or [],  # Don't inherit dependencies
            authors=authors or ManifestAuthorList(self.authors._authors.copy()),
            maintainers=maintainers or ManifestMaintainerList(self.maintainers._authors.copy()),
            copyright=copyright or self.copyright,
            license=license or self.license,
            status=status or self.status
        )


# Core authors for use in own manifest
_manifest_core_authors = ManifestAuthorList([
    ManifestAuthor(tag="rraudzus", 
        name="Rouven Raudzus", 
        email="raudzus@autiwire.org", 
        company="AutiWire GmbH", 
        since_version="0.0.0", 
        since_date=datetime.date(2025,5,10))
        ])    


# Core maintainers, initially same as authors
_manifest_core_maintainers = ManifestMaintainerList(_manifest_core_authors._authors.copy())


# Define Manifests own manifest
Manifest.__manifest__ = Manifest(
    location=Manifest.Location(module=__name__, classname=Manifest.__qualname__),
    description="Base class for all manifests",    
    status=Manifest.Status.Development,
    dependencies=[],
    authors=_manifest_core_authors,
    maintainers=_manifest_core_maintainers,
    copyright=Manifest.Copyright(date=datetime.date(2025,5,18), author=_manifest_core_authors.rraudzus),
    license=Manifest.licenses.NoLicense,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=datetime.date(2025,5,18), author=_manifest_core_authors.rraudzus, 
                            notes=["Initial release"]),
        Manifest.Changelog(version="0.1.1", date=datetime.date(2025,5,19), author=_manifest_core_authors.rraudzus, 
                            notes=["Added maintainers"]),
        Manifest.Changelog(version="0.1.2", date=datetime.date(2025,5,20), author=_manifest_core_authors.rraudzus, 
                            notes=["Added license"]),
        Manifest.Changelog(version="0.1.3", date=datetime.date(2025,5,21), author=_manifest_core_authors.rraudzus, 
                            notes=["Modified location information, requires less parameters"]),
        Manifest.Changelog(version="0.1.4", date=datetime.date(2025,5,22), author=_manifest_core_authors.rraudzus, 
                            notes=["Moved _manifest_core_* from class to module for more compactness"]),
        Manifest.Changelog(version="0.1.5", date=datetime.date(2025,5,23), author=_manifest_core_authors.rraudzus, 
                            notes=["Added doc property to get the docstring of the class or module"]),
    ]
)

