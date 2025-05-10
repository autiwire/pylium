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
        processor=lambda cls: cls.changelog[-1].version if cls.changelog and isinstance(cls.changelog, list) and len(cls.changelog) > 0 and hasattr(cls.changelog[-1], 'version') else "0.0.0",
        requires=["changelog"]
    )
    description: ClassVar[str] = Attribute(
        processor=lambda cls: cls.__doc__.strip() if hasattr(cls, '__doc__') and isinstance(cls.__doc__, str) else ""
    )

    # Only add dependencies to files which are Role.HEADER or Role.IMPLEMENTATION
    # Headers are for defining and installing dependencies, implementations are for using them
    dependencies: ClassVar[List[Dependency]] = Attribute(
        processor=lambda cls: _ModuleBase._process_additive_dependencies(cls),
        requires=["file", "role"],
        always_run_processor=True # Ensure additive logic always runs
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

        # Attributes whose processors (if defined on _ModuleBase) should always be re-evaluated for each subclass,
        # rather than just inheriting a concrete value from an intermediate parent.
        attrs_that_always_reprocess_processor = {
            "version", "name", "file", "fqn", "role", "description", "dependencies"
        }

        for attr_name in ordered_attrs_to_resolve:
            # Priority 1: Check if the attribute is one that must always re-run its _ModuleBase processor.
            if attr_name in attrs_that_always_reprocess_processor:
                original_descriptor_on_base = _ModuleBase.__dict__.get(attr_name)
                # DIAGNOSTIC: What is original_descriptor_on_base for 'dependencies'?
                # if attr_name == 'dependencies':
                #     logger.debug(f"  INIT_SUBCLASS ({cls.__name__}): For 'dependencies', _ModuleBase.__dict__.get('dependencies') is: {original_descriptor_on_base}, type: {type(original_descriptor_on_base)}")
                
                if isinstance(original_descriptor_on_base, _ModuleBase.Attribute):
                    resolved_value = original_descriptor_on_base.__get__(None, cls) # This calls the attribute's processor
                    setattr(cls, attr_name, resolved_value)
                    # if attr_name == 'dependencies': # DIAGNOSTIC
                    #     logger.debug(f"  POST-SETATTR (always_reprocess) for {cls.__name__}.dependencies: value in __dict__ is {cls.__dict__.get('dependencies')}") # DIAGNOSTIC
                    continue # Value set, move to next attribute
                else:
                    # Config error: listed for reprocessing but not a _ModuleAttribute on _ModuleBase.
                    logger.warning(
                        f"Configuration warning: Attribute '{attr_name}' in 'attrs_that_always_reprocess_processor' "
                        f"but not a _ModuleAttribute on _ModuleBase. Falling back for {cls.__name__}."
                    )
                    # Fall through to standard handling below
            
            # Priority 2: If not always reprocessed, check for explicit concrete value on cls.
            val_explicitly_on_cls = cls.__dict__.get(attr_name)
            if val_explicitly_on_cls is not None and not isinstance(val_explicitly_on_cls, _ModuleBase.Attribute):
                setattr(cls, attr_name, val_explicitly_on_cls)
                # if attr_name == 'dependencies': # DIAGNOSTIC
                #     logger.debug(f"  POST-SETATTR (explicit_on_cls) for {cls.__name__}.dependencies: value in __dict__ is {cls.__dict__.get('dependencies')}") # DIAGNOSTIC
                continue # Value set, move to next attribute

            # Priority 3: Standard MRO-based resolution (inherited concrete value or resolve inherited/own descriptor).
            value_via_mro = getattr(cls, attr_name)
            if isinstance(value_via_mro, _ModuleBase.Attribute):
                # Attribute is still a descriptor; resolve it.
                descriptor_to_resolve = value_via_mro
                resolved_value = descriptor_to_resolve.__get__(None, cls)
                setattr(cls, attr_name, resolved_value)
            else:
                # Attribute is an inherited concrete value; use it.
                setattr(cls, attr_name, value_via_mro)
            
            # if attr_name == 'dependencies': # DIAGNOSTIC for the MRO path
            #     logger.debug(f"  POST-SETATTR (mro_fallback) for {cls.__name__}.dependencies: value in __dict__ is {cls.__dict__.get('dependencies')}") # DIAGNOSTIC


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

    @staticmethod
    def _process_additive_dependencies(cls) -> List[Dependency]:
        # logger.debug(f"_process_additive_dependencies for {cls.__name__}")
        parent_deps_list = []
        # Iterate MRO starting from the first parent (cls.__mro__[1])
        for base in cls.__mro__[1:]:
            if not issubclass(base, _ModuleBase):
                if base is object: # Stop if we are beyond _ModuleBase hierarchy
                    break
                continue # Skip non-_ModuleBase intermediate classes (e.g., ABC)
            
            # Try to get the already resolved list directly from the parent's __dict__ first.
            # This assumes __init_subclass__ has already processed the base and set a concrete list.
            resolved_deps_on_base = base.__dict__.get('dependencies') 

            # logger.debug(f"  _process_additive_dependencies ({cls.__name__}): Checking base {base.__name__}.__dict__.get('dependencies'): type={type(resolved_deps_on_base)}, value={resolved_deps_on_base}") # DIAGNOSTIC

            if isinstance(resolved_deps_on_base, list):
                parent_deps_list = list(resolved_deps_on_base) # Make a copy
                # logger.debug(f"  _process_additive_dependencies ({cls.__name__}): Found parent_deps_list from {base.__name__}.__dict__: {parent_deps_list}")
                break # Found the nearest parent's list
            else:
                 # Fallback if not in __dict__ (e.g. _ModuleBase itself which has the descriptor)
                 # or if it was in __dict__ but not a list (should not happen if baking works)
                fallback_deps_on_base = getattr(base, 'dependencies', None)
                # logger.debug(f"  _process_additive_dependencies ({cls.__name__}): Fallback getattr(base, 'dependencies') for {base.__name__}: type={type(fallback_deps_on_base)}, value={fallback_deps_on_base}") # DIAGNOSTIC
                if isinstance(fallback_deps_on_base, list):
                    parent_deps_list = list(fallback_deps_on_base)
                    # logger.debug(f"  _process_additive_dependencies ({cls.__name__}): Found parent_deps_list from getattr({base.__name__}): {parent_deps_list}")
                    break

            if base is _ModuleBase: 
                # logger.debug(f"  _process_additive_dependencies ({cls.__name__}): Reached _ModuleBase or equivalent stopping point. parent_deps_list is {parent_deps_list}")
                break
        
        own_deps_list = []
        if 'dependencies' in cls.__dict__:
            val_in_dict = cls.__dict__['dependencies']
            if isinstance(val_in_dict, list):
                own_deps_list = val_in_dict
                # logger.debug(f"  _process_additive_dependencies: Found own_deps_list in {cls.__name__}.__dict__: {own_deps_list}")
            else:
                # logger.debug(f"  _process_additive_dependencies: '{cls.__name__}.dependencies' in __dict__ but not a list (type: {type(val_in_dict)}). Treating as no 'own' new deps.")
                pass
        
        final_list = parent_deps_list + own_deps_list
        # logger.debug(f"  _process_additive_dependencies: Final deps for {cls.__name__}: {final_list}")
        return final_list