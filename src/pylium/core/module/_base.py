from ._meta import _ModuleMeta
from ._attrs import _ModuleType, _ModuleRole, _ModuleAttribute, _ModuleDependency, _ModuleAuthorInfo, _ChangelogEntry

from abc import ABC
import sys
import os
from typing import ClassVar, List, Optional, Type, Any

from logging import getLogger
logger = getLogger(__name__)

class _ModuleBase(ABC, metaclass=_ModuleMeta):
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
    version: ClassVar[str] = Attribute(
        processor=lambda cls: cls.changelog[0].version if cls.changelog and isinstance(cls.changelog, list) and len(cls.changelog) > 0 and hasattr(cls.changelog[0], 'version') else "0.0.0",
        requires=["changelog"]
    )
    description: ClassVar[str] = Attribute(
        processor=lambda cls: cls.__doc__.strip() if hasattr(cls, '__doc__') and isinstance(cls.__doc__, str) else ""
    )
    dependencies: ClassVar[List[Dependency]] = Attribute(
        default_factory=list
    )
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
        # Processor and requires removed, will now enforce explicit setting in concrete subclasses
        default=Type.NONE 
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
            "name", "file", "description", "dependencies", 
            "authors", "changelog", "version", "fqn", "type", "role"
        ]

        for attr_name in ordered_attrs_to_resolve:
            val_directly_on_cls = cls.__dict__.get(attr_name)

            if val_directly_on_cls is not None and not isinstance(val_directly_on_cls, _ModuleBase.Attribute):
                # Case 1: cls explicitly defines a concrete value.
                # Ensure it's set on the class. If it was a simple ClassVar = value, it's already effectively there.
                # For consistency and to ensure "baking", we can do setattr.
                setattr(cls, attr_name, val_directly_on_cls)
            else:
                # Case 2: cls does not define an explicit concrete value in its __dict__,
                # OR val_directly_on_cls is an _ModuleAttribute instance (cls redefines the descriptor).
                
                # Get the value as Python sees it via MRO. This could be:
                # - a concrete value inherited from a parent (e.g., Module.type = Type.MODULE)
                # - a descriptor instance (e.g., _ModuleBase.description if not overridden)
                # - the descriptor instance defined on cls itself (if val_directly_on_cls was a descriptor)
                value_via_mro = getattr(cls, attr_name)

                if isinstance(value_via_mro, _ModuleBase.Attribute):
                    # The attribute on cls (via MRO) is still a _ModuleAttribute descriptor.
                    # This means it's the one from _ModuleBase, or one defined in an intermediate parent,
                    # or one defined in cls itself (if val_directly_on_cls was an Attribute instance).
                    # We resolve *this specific descriptor instance* for cls.
                    descriptor_to_resolve = value_via_mro
                    resolved_value = descriptor_to_resolve.__get__(None, cls)
                    setattr(cls, attr_name, resolved_value)
                else:
                    # It's a concrete value, inherited from a parent (e.g., CustomModule inherits Module.type).
                    # Bake this inherited concrete value onto cls.
                    setattr(cls, attr_name, value_via_mro)

        # After all attributes are resolved, check for mandatory 'type' in concrete subclasses
        # __abstractmethods__ is a frozenset of names of abstract methods.
        # It's empty for concrete classes.
        # We also check hasattr for __abstractmethods__ for robustness during class creation.
        if hasattr(cls, "__abstractmethods__") and not cls.__abstractmethods__ and \
           hasattr(cls, 'type') and cls.type == _ModuleBase.Type.NONE:
            raise TypeError(
                f"Concrete class '{cls.__name__}' must explicitly define the 'type' attribute. "
                f"It cannot be '{_ModuleBase.Type.NONE}'."
            )

    def __init__(self, *args, **kwargs):
        """
        Initialize the Module.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name} (Type: {self.type}, FQN: {self.fqn}, Version: {self.version})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.type}', fqn='{self.fqn}', file='{self.file}', version='{self.version}')"