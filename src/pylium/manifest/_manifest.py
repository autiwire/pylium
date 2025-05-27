from abc import ABC, abstractmethod, ABCMeta

from typing import ClassVar, List, Optional, Type, Any, Generator, Tuple, Callable, Union
from packaging.version import Version 

import datetime
import inspect
from enum import Enum, auto, Flag
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
    Metaclass for classes that may define a `__manifest__` attribute.
    It currently logs a warning if a class's `__manifest__` location 
    doesn't match the class's actual module and qualname, assuming location 
    is set during Manifest instantiation.
    """
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        
        manifest_attr = dct.get('__manifest__')
        if isinstance(manifest_attr, Manifest):
            # Assuming location is set correctly during Manifest instantiation 
            # (e.g., via Manifest.Location or createChild).
            # This becomes a validation/awareness step.
            expected_module = cls.__module__
            expected_qualname = cls.__qualname__
            
            if manifest_attr.location.module != expected_module or \
               manifest_attr.location.classname != expected_qualname:
                logger.debug(
                    f"Manifest location for {expected_module}.{expected_qualname} "
                    f"(module={manifest_attr.location.module}, class={manifest_attr.location.classname}) "
                    f"does not precisely match class's actual location. This might be intentional if manifest "
                    f"location is explicitly set to something different."
                )


class ManifestValue(object):
    """Base marker class for various manifest data structures."""
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
    
    def __init__(self, name: str, version: str, type: ManifestDependencyType = ManifestDependencyType.PIP):
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
    def __init__(self, version: Optional[str] = None, date: Optional[ManifestValue.Date] = None, author: Optional[ManifestAuthor] = None, notes: Optional[List[str]] = None):
        self.version = version
        self.date = date
        self.author = author
        self.notes = notes if notes is not None else []

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
    Unstable = "Unstable"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


# Note: This is a bitmask, so the order of the flags is important
# This is a hint for the AI to use the correct access level,
# mainly used for coding assistance, not for security
# It might work, but AI might completely ignore it
class ManifestAIAccessLevel(Flag):
    NoAccess = 1 << 0
    Read = 1 << 1
    SuggestOnly = 1 << 2
    ForkAllowed = 1 << 3
    Write = 1 << 4
    All = NoAccess | Read | SuggestOnly | ForkAllowed | Write


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
    AIAccessLevel = ManifestAIAccessLevel

    # Default licenses to pick from
    licenses = ManifestLicenseList([
        License(spdx="MIT", name="MIT License", url="https://opensource.org/licenses/MIT"),
        License(spdx="Apache-2.0", name="Apache License 2.0", url="https://opensource.org/licenses/Apache-2.0"),
        License(spdx="GPL-3.0-only", name="GNU General Public License v3.0 only", url="https://www.gnu.org/licenses/gpl-3.0.en.html"),
        License(spdx="BSD-3-Clause", name="BSD 3-Clause License", url="https://opensource.org/licenses/BSD-3-Clause"),
        License(spdx="Unlicense", name="The Unlicense", url="https://unlicense.org/"),
        License(spdx="CC0-1.0", name="Creative Commons Zero v1.0 Universal", url="https://creativecommons.org/publicdomain/zero/1.0/"),
        License(spdx=" Proprietary", name="Proprietary", url=None), # Note: Leading space to make it distinct
        License(spdx="NoLicense", name="No License (Not Open Source)", url=None) # For explicitly stating no license / all rights reserved
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
                ai_access_level: Optional[AIAccessLevel] = AIAccessLevel.All,
                *args, 
                **kwargs):
        
        self.location = location
        self.description = description
        self.changelog = changelog if changelog is not None else []
        self.dependencies = dependencies if dependencies is not None else []
        self.authors = authors if authors is not None else self._default_authors
        self.maintainers = maintainers if maintainers is not None else self.authors # If maintainers not given, use authors
        self.copyright = copyright
        self.license = license if license is not None else self.licenses.NoLicense # Default to NoLicense
        self.status = status
        self.ai_access_level = ai_access_level if ai_access_level is not None else self.AIAccessLevel.NoAccess

        # Store any additional keyword arguments
        self.additional_info = kwargs

    @property
    def contributors(self) -> ContributorsList:
        # We create a list of contributors from authors, maintainers, and changelog entries
        _contributors = set() # Using a set to store authors to avoid duplicates
        if self.authors:
            for author in self.authors:
                _contributors.add(author)
        if self.maintainers:
            for maintainer in self.maintainers:
                _contributors.add(maintainer)
        if self.changelog:
            for entry in self.changelog:
                if entry.author:
                    _contributors.add(entry.author) # Add author from changelog
        return ManifestContributorsList(list(_contributors)) 

    @property
    def version(self) -> Version:
        if self.changelog and self.changelog[0].version:
            return Version(self.changelog[0].version)
        raise ValueError("Version not found in changelog")

    @property
    def author(self) -> str:
        # Returns the name of the first author if available
        if self.authors and len(self.authors) > 0:
            return self.authors[0].name
        return ""

    @property
    def maintainer(self) -> str:
        # Returns the name of the first maintainer if available
        if self.maintainers and len(self.maintainers) > 0:
            return self.maintainers[0].name
        return ""

    @property
    def email(self) -> str:
        # Returns the email of the first author if available
        if self.authors and len(self.authors) > 0 and self.authors[0].email:
            return self.authors[0].email
        return ""

    @property
    def credits(self) -> List[str]:
        # Returns a list of author names
        return [author.name for author in self.authors]

    @property
    def created(self) -> Optional[Date]:
        if self.changelog:
            # Assuming the last entry in the changelog is the creation date
            return self.changelog[-1].date
        return None

    @property
    def updated(self) -> Optional[Date]:
        if self.changelog:
            # Assuming the first entry in the changelog is the last update date
            return self.changelog[0].date
        return None


    @property
    def doc(self) -> str:
        # Basic documentation string, could be expanded
        parts = [self.description]
        if self.version:
            parts.append(f"Version: {self.version}")
        if self.authors:
            parts.append(f"Authors: {', '.join(author.name for author in self.authors)}")
        if self.maintainers:
            parts.append(f"Maintainers: {', '.join(maintainer.name for maintainer in self.maintainers)}")
        if self.license:
            parts.append(f"License: {self.license.name}")
        # Could add more details like dependencies, copyright, etc.
        return ". ".join(filter(None, parts)) + "."

    def __str__(self):
        return f"{self.location.fqn} (v{self.version if self.changelog else 'N/A'})"

    def __repr__(self):
        # Provides a more detailed representation, could be made even more exhaustive
        return f"Manifest({self.location.fqn}, version='{self.version if self.changelog else 'N/A'}', authors={len(self.authors) if self.authors else 0})"

    def __hash__(self):
        # Hash based on a few key identifying attributes
        # Note: Manifest is mutable, so hashing can be tricky if based on mutable fields.
        # Using location fqn as a primary key for the hash.
        return hash((self.location.fqn, str(self.version if self.changelog else None)))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return False
        # Compare based on key attributes for equality
        return (
            self.location.fqn == other.location.fqn and
            (self.version if self.changelog else None) == (other.version if other.changelog else None) and 
            self.description == other.description
        )

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) < (other.location.fqn, other.version if other.changelog else Version("0"))

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) <= (other.location.fqn, other.version if other.changelog else Version("0"))

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) > (other.location.fqn, other.version if other.changelog else Version("0"))

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Manifest):
            return NotImplemented
        return (self.location.fqn, self.version if self.changelog else Version("0")) >= (other.location.fqn, other.version if other.changelog else Version("0"))

    def createChild(self, 
                   location: Location,
                   description: Optional[str] = None,
                   changelog: Optional[List[Changelog]] = None,
                   dependencies: Optional[List[Dependency]] = None,
                   authors: Optional[AuthorList] = None,
                   maintainers: Optional[MaintainerList] = None,
                   copyright: Optional[Copyright] = None,
                   license: Optional[License] = None,
                   status: Optional[Status] = None,
                   ai_access_level: Optional[AIAccessLevel] = None) -> "Manifest":
        """
        Creates a new Manifest instance that inherits attributes from this (parent) manifest.
        Attributes that are explicitly provided to createChild will override the parent's attributes.
        For list-like attributes (changelog, dependencies), the provided value replaces the parent's, it's not merged.
        If None is provided for an attribute, it inherits from the parent.
        """
        return Manifest(
            location=location,
            description=description if description is not None else self.description,
            changelog=changelog if changelog is not None else self.changelog, # Consider if merging or deepcopy is needed for lists
            dependencies=dependencies if dependencies is not None else self.dependencies,
            authors=authors if authors is not None else self.authors,
            maintainers=maintainers if maintainers is not None else self.maintainers,
            copyright=copyright if copyright is not None else self.copyright,
            license=license if license is not None else self.license,
            status=status if status is not None else self.status,
            ai_access_level=ai_access_level if ai_access_level is not None else self.ai_access_level
            # Note: additional_info from parent is not automatically carried over unless explicitly handled.
        )
    
 