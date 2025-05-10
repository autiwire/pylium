from ._meta import _ModuleMeta
from ._attrs import _ModuleType, _ModuleRole, _ModuleAttribute, _ModuleDependency, _ModuleAuthorInfo, _ChangelogEntry

from abc import ABC
import sys
import os
from typing import ClassVar, List, Optional, Type

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
                # It could be an inherited concrete value, or an inherited descriptor.
                
                current_value_on_cls = getattr(cls, attr_name) # How Python sees it via MRO

                if isinstance(current_value_on_cls, _ModuleBase.Attribute):
                    # It's still a descriptor when looked up on cls. This means it's the original
                    # descriptor from _ModuleBase, and no intermediate parent (like Module)
                    # has set a concrete value for it yet that CustomModule would inherit directly.
                    # So, we need to resolve it for 'cls'.
                    original_descriptor = current_value_on_cls 
                    value_to_set = original_descriptor.__get__(None, cls)
                    setattr(cls, attr_name, value_to_set)
                    descriptor_found = True
                else:
                    # getattr(cls, attr_name) returned a concrete value. This means 'cls'
                    # either defined it concretely (already handled by the 'if' above, but defensive)
                    # or an intermediate parent (like Module) defined it concretely, and 'cls'
                    # is inheriting that concrete value. We should respect this inherited concrete value.
                    # No explicit setattr(cls,...) needed here, as standard inheritance handles it.
                    # We just mark it as "handled" for our loop.
                    descriptor_found = True 

            if not descriptor_found:
                 logger.warning(f"Could not find or resolve attribute '{attr_name}' for {cls.__name__}")

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
        return f"{self.__class__.__name__}: {self.name} (Type: {self.type}, FQN: {self.fqn})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.type}', fqn='{self.fqn}', file='{self.file}')"