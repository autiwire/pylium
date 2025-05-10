from typing import List, ClassVar, Optional, Any, Callable
from enum import Enum
from abc import ABC, abstractmethod
import dataclasses
import os
import sys
import datetime

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
    version: str
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
    
class _ModuleBase(ABC):
    """
    An abstract base class for all pylium modules.
    """
   
    Type = _ModuleType
    Role = _ModuleRole
    Attribute = _ModuleAttribute
    Dependency = _ModuleDependency
    AuthorInfo = _ModuleAuthorInfo
    ChangelogEntry = _ChangelogEntry # Expose for type hinting / usage

    # Attributes managed by descriptors
    version: ClassVar[str] = Attribute(default="0.0.0")
    description: ClassVar[str] = Attribute(
        processor=lambda cls: cls.__doc__.strip() if hasattr(cls, '__doc__') and isinstance(cls.__doc__, str) else ""
    )
    dependencies: ClassVar[List[Dependency]] = Attribute(default_factory=list)
    authors: ClassVar[List[AuthorInfo]] = Attribute(default_factory=list)
    changelog: ClassVar[List[ChangelogEntry]] = Attribute(default_factory=list)

    # Core identity attributes also managed by ModuleAttribute
    name: ClassVar[str] = Attribute(processor=lambda cls: cls.__module__)
    file: ClassVar[Optional[str]] = Attribute(
        processor=lambda cls: (
            sys.modules.get(cls.__module__).__file__ 
            if sys.modules.get(cls.__module__) and 
               hasattr(sys.modules.get(cls.__module__), '__file__') and 
               sys.modules.get(cls.__module__).__file__ is not None 
            else None
        )
    )
    fqn: ClassVar[str] = Attribute(
        processor=lambda cls: f"{cls.name}.__init__" if cls.file and os.path.basename(cls.file) == "__init__.py" else cls.name,
        requires=["name", "file"]
    )
    type: ClassVar[Type] = Attribute(
        processor=lambda cls: (
            _ModuleBase.Type.PACKAGE if cls.file and os.path.basename(cls.file) == "__init__.py" 
            else _ModuleBase.Type.MODULE if cls.file 
            else _ModuleBase.Type.NONE
        ),
        requires=["file"]
    )
    role: ClassVar[Role] = Attribute(
        processor=lambda cls: (
            _ModuleBase.Role.HEADER if cls.file and cls.file.endswith("_h.py") else
            _ModuleBase.Role.IMPLEMENTATION if cls.file and cls.file.endswith("_impl.py") else
            _ModuleBase.Role.BUNDLE if cls.file and cls.file.endswith(".py") else
            _ModuleBase.Role.NONE
        ),
        requires=["file"]
    )

    def __init_subclass__(cls, **kwargs) -> None:
        logger.debug(f"Module __init_subclass__ for: {cls.__name__}")
        super().__init_subclass__(**kwargs)

        ordered_attrs_to_resolve = [
            "name", "file", "version", "description", "dependencies", 
            "authors", "changelog", "fqn", "type", "role"
        ]

        for attr_name in ordered_attrs_to_resolve:
            # Find the ModuleAttribute descriptor instance. It should be on _ModuleBase
            # or one of its direct bases if we change where these are defined.
            # For simplicity, assuming they are on a known base or discoverable.
            # We need to ensure we are calling the __get__ of the *original descriptor*.
            
            descriptor_found = False
            value_to_set = None

            # Check if attr_name is explicitly defined in cls body and is NOT a ModuleAttribute itself.
            # If so, that value takes precedence and descriptor logic is skipped for this cls.
            if attr_name in cls.__dict__ and not isinstance(cls.__dict__[attr_name], _ModuleBase.Attribute):
                # This attribute was explicitly overridden with a concrete value in the subclass body.
                # No need to call descriptor; getattr will just return this value.
                # We still call getattr once to ensure it's properly part of the class state if needed,
                # though for simple ClassVars it's already there.
                _ = getattr(cls, attr_name)
                descriptor_found = True # Mark as handled, even if not by our descriptor path
            else:
                # Find the descriptor from _ModuleBase (or an appropriate parent in MRO)
                # This ensures we are not getting a resolved value from an intermediate class like Module.
                original_descriptor = None
                for mro_cls in cls.mro():
                    if mro_cls is object: continue
                    if attr_name in mro_cls.__dict__ and isinstance(mro_cls.__dict__[attr_name], _ModuleBase.Attribute):
                        original_descriptor = mro_cls.__dict__[attr_name]
                        break
                
                if original_descriptor:
                    descriptor_found = True
                    # Call the original descriptor's __get__ method, with 'cls' as the owner.
                    # The descriptor will calculate the value specific to 'cls'.
                    value_to_set = original_descriptor.__get__(None, cls)
                    # Now, explicitly set this resolved value onto 'cls.__dict__'.
                    # This "bakes" the value for this specific subclass.
                    setattr(cls, attr_name, value_to_set)
                elif hasattr(cls, attr_name):
                    # Fallback: Attribute exists but is not a ModuleAttribute we found on a base.
                    # This might be an already resolved value or a normal ClassVar.
                    # Just access it to ensure any standard Python mechanisms run.
                    _ = getattr(cls, attr_name) 
                    descriptor_found = True # Mark as handled

            if not descriptor_found:
                 logger.warning(f"Could not find or resolve attribute '{attr_name}' for {cls.__name__}")

    def __init__(self, *args, **kwargs):
        """
        Initialize the Module.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name} (Type: {self.type}, FQN: {self.fqn})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.type}', fqn='{self.fqn}', file='{self.file}')"

class Module(_ModuleBase):
    """
    A module represented by a single Python (.py) file.
    """
    type: ClassVar[_ModuleBase.Type] = _ModuleBase.Type.MODULE
    version: ClassVar[str] = "0.0.1"

__all__ = ["Module"]