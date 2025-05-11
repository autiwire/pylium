import dataclasses
from typing import Any, Callable, Optional, List
import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

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
    always_run_processor: bool = False # If True, processor is called even if an explicit value exists in class __dict__
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
        
        # If a processor exists AND always_run_processor is True, the processor takes full control.
        # It is then responsible for how it incorporates any explicit values from owner_cls.__dict__.
        if self.processor and self.always_run_processor:
            return self.processor(owner_cls)
        
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
    

    def __str__(self):
        return f"{self._public_name} = {self.default!r}"

    def __repr__(self):
        details = []
        # Use a sentinel for default to distinguish from None if None is a valid default
        _sentinel = object()
        if getattr(self, 'default', _sentinel) is not _sentinel and self.default is not None: # Check self.default is not None to avoid logging default=None
            details.append(f"default={self.default!r}")
        if hasattr(self, '_default_factory') and self._default_factory is not None:
            details.append(f"default_factory={self._default_factory.__name__ if hasattr(self._default_factory, '__name__') else repr(self._default_factory)}")
        if hasattr(self, 'processor') and self.processor is not None:
            details.append(f"processor={self.processor.__name__ if hasattr(self.processor, '__name__') else repr(self.processor)}")
        if hasattr(self, 'requires') and self.requires:
            details.append(f"requires={self.requires!r}")
        if hasattr(self, 'always_run_processor') and self.always_run_processor:
            details.append(f"always_run_processor={self.always_run_processor!r}")
        return f"<_ModuleAttribute({', '.join(details)}) at 0x{id(self):x}>"