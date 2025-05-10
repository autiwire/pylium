import dataclasses
from typing import Any, Callable, Optional, List
import datetime
from enum import Enum

@dataclasses.dataclass(frozen=True)
class _ModuleDependencyType(Enum):
    PYLIUM = "pylium"
    PIP = "pip"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

@dataclasses.dataclass(frozen=True)
class _ModuleDependency:
    """
    A dependency for a module.
    """

    Type = _ModuleDependencyType

    name: str
    type: Type
    version: str

    def __str__(self):
        return f"{self.name} ({self.type}) {self.version}"
    
    def __repr__(self):
        return f"{self.name} ({self.type}) {self.version}"
    
@dataclasses.dataclass(frozen=True)
class _ModuleAuthorInfo:
    name: str
    email: Optional[str] = None
    since_version: Optional[str] = None
    since_date: Optional[datetime.date] = None

    def __str__(self):
        return f"{self.name} ({self.email}) {self.since_version} {self.since_date}"
    
    def __repr__(self):
        return f"{self.name} ({self.email}) [since: {self.since_version} @ {self.since_date}]"

@dataclasses.dataclass(frozen=True)
class _ChangelogEntry:
    version: Optional[str] = None
    notes: List[str] = dataclasses.field(default_factory=list)
    date: Optional[datetime.date] = None
    
    def __str__(self):
        return f"{self.version} ({self.date}) {self.notes}"

    def __repr__(self):
        return f"{self.version} ({self.date}) {self.notes}"

class _ModuleType(Enum):
    NONE = "none"
    MODULE = "module"
    PACKAGE = "package"
    PROJECT = "project"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value

class _ModuleRole(Enum):
    NONE = "none"
    HEADER = "header"
    IMPLEMENTATION = "implementation"
    BUNDLE = "bundle"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value

@dataclasses.dataclass
class _ModuleAttribute:
    """
    A descriptor to manage the initialization of class variables for _ModuleBase subclasses.
    It allows for a declarative way to specify how a class variable's value should be
    determined, looking at explicit subclass definitions, a context-aware processor,
    or defaults. On first access, it resolves the value and replaces itself 
    on the owner class with this resolved value.
    """
    default: Any = None
    default_factory: Optional[Callable[[], Any]] = None
    processor: Optional[Callable[[type], Any]] = None # processor(owner_cls) -> value
    requires: Optional[List[str]] = None # Names of other ModuleAttributes this one depends on
    _public_name: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        if self.default is not None and self.default_factory is not None:
            raise ValueError("Cannot specify both default and default_factory for ModuleAttribute.")
        if self.processor is not None and (self.default is not None or self.default_factory is not None):
            raise ValueError("Cannot specify processor along with default/default_factory. Processor is the source if no explicit override.")

    def __set_name__(self, owner_cls: type, name: str):
        self._public_name = name

    def __get__(self, instance: Optional[object], owner_cls: type) -> Any:
        if owner_cls is None: # Being accessed on an instance
            if instance is None: return self # Should not happen if owner_cls is also None
            owner_cls = type(instance)
            # For instance access, we could choose to cache on instance, or always re-delegate to class
            # For ClassVar-like behavior, we delegate to class resolution logic.
            # However, to allow instance-specific caching if desired later: result = owner_cls.__dict__.get(...) etc.

        # Logic for class access (owner_cls is the class itself)
        
        # 1. Check for an explicit, non-descriptor override in the owner_cls's __dict__
        #    This handles cases like `version = "1.0.0"` in a subclass body.
        #    The `val_from_dict is not self` check is crucial if the attribute in owner_cls.__dict__ 
        #    could be the descriptor itself (e.g. if owner_cls is _ModuleBase).
        val_from_dict = owner_cls.__dict__.get(self._public_name)
        if val_from_dict is not None and val_from_dict is not self:
            return val_from_dict

        # 2. If no explicit override, calculate value using processor or defaults.
        #    This calculated value is specific to this owner_cls.
        value: Any
        if self.processor:
            value = self.processor(owner_cls)
        elif self.default_factory is not None:
            value = self.default_factory()
        else:
            value = self.default
        
        # The descriptor itself does NOT set the attribute on owner_cls here.
        # It just returns the computed/resolved value for this owner_cls.
        # __init_subclass__ will be responsible for setattr-ing this onto the class.
        return value
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.type}', fqn='{self.fqn}', file='{self.file}')"