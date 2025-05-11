from ._meta import _ModuleMeta
from ._attrs import _ModuleType, _ModuleRole, _ModuleAttribute, _ModuleDependency, _ModuleAuthorInfo, _ChangelogEntry

from abc import ABC
import sys
import os
from typing import ClassVar, List, Optional, Type, Any, Generator
import pkgutil
import importlib
import typing

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
    
    @classmethod
    def list(cls) -> List[typing.Type["_ModuleBase"]]:
        """
        Return a list of all subclasses of this class (including the class itself if applicable)
        found by scanning defined module source directories.

        Source directories are determined by PYLIUM_MODULE_DIRS environment variable,
        or by a default calculated from the 'pylium' package location.

        It walks these directories, imports .py files (excluding '_impl.py'),
        and checks for classes that are subclasses of 'cls' and defined within that submodule.
        If a module defines multiple such subclasses, a warning is logged, and all are included.
        """
        found_module_types: List[typing.Type["_ModuleBase"]] = []
        module_src_roots_to_scan: List[str] = []

        # Determine source roots dynamically
        default_src_root = None
        try:
            pylium_module = sys.modules['pylium']
            if hasattr(pylium_module, '__file__') and pylium_module.__file__:
                # Assuming pylium.__file__ might be .../src/pylium/__init__.py
                # or .../site-packages/pylium/__init__.py
                # We want to get to the directory containing 'pylium' (e.g., 'src/' or 'site-packages/')
                pylium_pkg_dir = os.path.dirname(pylium_module.__file__)
                default_src_root = os.path.abspath(os.path.join(pylium_pkg_dir, '..'))
            else:
                # If pylium is a namespace package without a file, this default logic might be harder.
                # Fallback: Try to find the 'src' directory if the current CWD is the project root.
                # This is a guess and might need refinement.
                cwd = os.getcwd()
                potential_src = os.path.join(cwd, "src")
                if os.path.isdir(potential_src):
                    default_src_root = potential_src
                else: # Last resort, use CWD, though this is broad
                    default_src_root = cwd 
                logger.debug(f"list: 'pylium' module has no __file__, guessed default_src_root: {default_src_root}")
        except KeyError:
            logger.warning("list: 'pylium' module not found in sys.modules. Default source root cannot be determined this way.")
            # As a last fallback, could use current working directory, or an empty list to rely solely on env var
            cwd = os.getcwd()
            potential_src = os.path.join(cwd, "src")
            if os.path.isdir(potential_src):
                default_src_root = potential_src
            else:
                default_src_root = cwd
            logger.debug(f"list: 'pylium' module not in sys.modules, guessed default_src_root for fallback: {default_src_root}")

        env_module_dirs_str = os.environ.get("PYLIUM_MODULE_DIRS")
        if env_module_dirs_str:
            module_src_roots_to_scan.extend([
                os.path.abspath(d.strip()) for d in env_module_dirs_str.split(os.pathsep) if d.strip()
            ])
            logger.debug(f"list: Using PYLIUM_MODULE_DIRS: {module_src_roots_to_scan}")
        elif default_src_root:
            module_src_roots_to_scan.append(default_src_root)
            logger.debug(f"list: Using default source root: {module_src_roots_to_scan}")
        else:
            logger.warning("list: No PYLIUM_MODULE_DIRS set and default source root could not be determined. Module scan might be empty or limited.")
            # No roots to scan, so return empty
            return []

        logger.debug(f"list: Starting scan for subclasses of '{cls.__name__}' using os.walk. "
                     f"Final source roots: {module_src_roots_to_scan}")

        for walk_root_dir in module_src_roots_to_scan:
            if not os.path.isdir(walk_root_dir):
                logger.warning(f"  list: Module source root directory not found or not a directory: '{walk_root_dir}'. Skipping.")
                continue
            
            logger.debug(f"  list: Walking directory: '{walk_root_dir}'")
            for subdir, dirs, files in os.walk(walk_root_dir):
                # Skip hidden directories and common non-code directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.venv', '.git', 'node_modules']]

                for file_name in files:
                    if not file_name.endswith(".py"):
                        continue
                    
                    if file_name.endswith("_impl.py"):
                        logger.debug(f"    list: Skipping impl file: '{os.path.join(subdir, file_name)}'")
                        continue

                    full_file_path = os.path.join(subdir, file_name)
                    
                    # Construct the Python module path
                    try:
                        # Relative path from the current walk_root_dir
                        relative_path_from_walk_root = os.path.relpath(full_file_path, walk_root_dir)
                    except ValueError: # pragma: no cover
                        # This can happen if full_file_path is not under walk_root_dir,
                        # though os.walk should ensure this.
                        logger.warning(f"    list: Could not determine relative path for '{full_file_path}' from '{walk_root_dir}'. Skipping.")
                        continue

                    module_name_parts = relative_path_from_walk_root[:-3].split(os.sep) # Remove .py and split
                    
                    if not module_name_parts: # pragma: no cover
                        logger.debug(f"    list: Skipping file '{full_file_path}', could not determine module parts.")
                        continue

                    if module_name_parts[-1] == "__init__":
                        module_name_to_import = ".".join(module_name_parts[:-1])
                        if not module_name_to_import: # Top-level __init__.py in a source root, might not be common.
                            logger.debug(f"    list: Skipping top-level __init__.py at '{full_file_path}' as module name is empty.")
                            continue
                    else:
                        module_name_to_import = ".".join(module_name_parts)
                    
                    # Ensure the module is in sys.path or discoverable by Python's import system
                    # This is often handled by how the project is structured and installed (e.g. editable install)
                    # or if walk_root_dir (or its parent) is in sys.path.
                    # If walk_root_dir is like '.../project/src', then modules like 'pylium.core' should be importable.
                    
                    logger.debug(f"    list: Attempting to import module: '{module_name_to_import}' from file '{full_file_path}'")
                    try:
                        module = importlib.import_module(module_name_to_import)
                        logger.debug(f"      list: Successfully imported '{module_name_to_import}'")
                    except ImportError as e:
                        logger.warning(f"      list: Could not import module '{module_name_to_import}' from '{full_file_path}': {e}. "
                                       f"Ensure the parent of '{module_name_parts[0]}' (derived from source root '{walk_root_dir}') is in sys.path.")
                        continue
                    except Exception as e: # Catch other potential import-related errors
                        logger.error(f"      list: Unexpected error importing module '{module_name_to_import}' from '{full_file_path}': {e}", exc_info=True)
                        continue
                    
                    defined_in_this_module: List[typing.Type["_ModuleBase"]] = []
                    for attr_name in dir(module):
                        try:
                            obj = getattr(module, attr_name)
                        except Exception:  # pragma: no cover
                            continue 

                        if isinstance(obj, type) and \
                           issubclass(obj, cls) and \
                           obj.__module__ == module_name_to_import: # Check it's defined in this module
                            logger.debug(f"        list: Found matching class '{obj.__name__}' in module '{module_name_to_import}'")
                            defined_in_this_module.append(obj)
                    
                    if len(defined_in_this_module) > 1:
                        logger.warning(
                            f"      list: Module '{module_name_to_import}' defines multiple subclasses of '{cls.__name__}': "
                            f"{[c.__name__ for c in defined_in_this_module]}. All will be included."
                        )
                    
                    found_module_types.extend(defined_in_this_module)

        logger.info(f"list: Completed scan for '{cls.__name__}'. Found {len(found_module_types)} matching module types: "
                    f"{[t.__module__ + '.' + t.__name__ for t in found_module_types]}")
        return found_module_types
