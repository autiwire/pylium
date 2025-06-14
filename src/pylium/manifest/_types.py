import datetime
from typing import Optional, List, Any, Generator
import importlib.util
from pathlib import Path

class ManifestValue(object):
    """Base marker class for various manifest data structures."""
    Date = datetime.date

    def __init__(self):
        pass


class ManifestLocation(ManifestValue):
    def __init__(self, module: str, classname: Optional[str] = None, funcname: Optional[str] = None):
        """
        Create a manifest location.
        
        Args:
            module: The module name:
                   - If modules: use __name__
                   - If classes: use __module__
            
            classname: Optional class name (typically __qualname__ for classes)

            funcname: Optional function name (typically __qualname__ for functions)

        """
        self.module = module
        self.classname = classname
        self.funcname = funcname

        # Get the file location from the module name
        spec = importlib.util.find_spec(self.module)
        if spec is None or spec.origin is None:
            raise ImportError(f"Could not find module {self.module}")
            
        self.file = str(Path(spec.origin).resolve())        
        if self.funcname and self.classname:
            self.fqn = f"{self.module}.{self.classname}.{self.funcname}"
        elif self.classname:
            self.fqn = f"{self.module}.{self.classname}"
        else:
            self.fqn = self.module

    @property
    def shortName(self) -> str:
        """Returns the module name with implementation suffixes removed."""
        remove_strs = [".__header__", ".__impl__", "_h", "_impl"]
        module_name = self.module
        for remove_str in remove_strs:
            if module_name.endswith(remove_str):
                return module_name[:-len(remove_str)]
        return module_name

    def __str__(self):
        return f"{self.fqn}"
    
    def __repr__(self):
        return f"{self.fqn} @ {self.file}"

    @property
    def isPackage(self) -> bool:
        """
        Checks if the location points to a package (and not a single .py file)
        """
        spec = importlib.util.find_spec(self.shortName)
        #print(f"DEBUG: spec: {spec}") # DEBUG
        #print(f"DEBUG: spec.submodule_search_locations: {spec.submodule_search_locations}") # DEBUG
        return spec is not None and spec.submodule_search_locations is not None
    
    @property
    def isModule(self) -> bool:
        """
        Checks if the location points to a module.
        """
        return self.classname is None and self.funcname is None

    @property
    def isClass(self) -> bool:
        """
        Checks if the location points to a class.
        """
        return self.classname is not None and self.funcname is None
    
    @property
    def isFunction(self) -> bool:
        """
        Checks if the location points to a function.
        """
        return self.funcname is not None

    @property
    def isMethod(self) -> bool:
        """
        Checks if the location points to a method.
        """
        return self.funcname is not None and self.classname is not None
    

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
ManifestContributorList = ManifestAuthorList


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
    

class ManifestDependency(ManifestValue):
    from ._enums import ManifestDependencyType as Type

    #Type = ManifestDependencyType
    
    def __init__(self, name: str, version: str, type: Type = Type.PIP):
        self.type = type
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name} ({self.version})"
    
    def __repr__(self):
        return f"{self.name} ({self.version})"