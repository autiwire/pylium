from ._meta import _ModuleMeta
from ._attrs import _ModuleType, _ModuleRole, _ModuleAttribute, _ModuleDependency, _ModuleAuthorInfo, _ChangelogEntry

from abc import ABC
import sys
import os
from typing import ClassVar, List, Optional, Type, Any, Generator, Tuple, Callable
import pkgutil
import importlib
import logging
import typing
import re 
import datetime

import logging
logger = logging.getLogger(__name__)

class _ModuleBase(ABC, metaclass=_ModuleMeta):
    """
    An abstract base class for all pylium modules.
    """
    Date = datetime.date
    Type = _ModuleType
    Role = _ModuleRole
    Attribute = _ModuleAttribute
    Dependency = _ModuleDependency
    AuthorInfo = _ModuleAuthorInfo
    ChangelogEntry = _ChangelogEntry # Expose for type hinting / usage

    @classmethod
    def class_role(cls, role: Role) -> Callable[[Type], Type]:
        """
        Class decorator to explicitly set the role of a class (HEADER/IMPLEMENTATION).
        This is used to mark classes as either header or implementation, which is a separate
        concept from the Module/Package/Project type system.

        Args:
            role: The role to assign to the class (should be HEADER or IMPLEMENTATION)
        
        Returns:
            A class decorator that sets the role
        """
        if role not in (cls.Role.HEADER, cls.Role.IMPLEMENTATION):
            raise ValueError(f"class_role decorator only accepts HEADER or IMPLEMENTATION roles, got {role}")
            
        def decorator(cls_to_decorate: Type) -> Type:
            # Store the role in a special class attribute
            logger.debug(f"class_role decorator: Setting __pylium_class_role__ for {cls_to_decorate.__name__} to {role}")
            setattr(cls_to_decorate, '__pylium_class_role__', role)
            return cls_to_decorate
        return decorator

    # Determine project root and path to pip2sysdep data
    # Assuming _base.py is at .../project_root/src/pylium/core/module/_base.py
    # And pip2sysdep is at .../project_root/external/pip2sysdep
    _module_base_file_dir = os.path.dirname(__file__)
    _project_root_dir = os.path.abspath(os.path.join(_module_base_file_dir, '..', '..', '..', '..'))
    _pip2sysdep_data_path: ClassVar[str] = os.path.join(_project_root_dir, 'external', 'pip2sysdep', 'data')
    
    logger.debug(f"_ModuleBase: Calculated project root for pip2sysdep: {_project_root_dir}")
    logger.debug(f"_ModuleBase: Path to pip2sysdep data: {_pip2sysdep_data_path}")

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
            getattr(cls, '__pylium_class_role__') if hasattr(cls, '__pylium_class_role__') else
            _ModuleBase.Role.NONE
        ),
        requires=["file"]
    )

    logger: ClassVar[logging.Logger] = Attribute(
        processor=lambda cls: logging.getLogger(cls.name),
        requires=["name"]
    )

    @classmethod
    def basename(cls) -> str:
        """
        Returns the basename of the module name without _h or _impl suffixes.
        """

        # Therefor remove ending _h or _impl from the name
        ret = cls.name
        if ret.endswith("._h"):
            ret = ret[:-3]
        elif ret.endswith("_h"):
            ret = ret[:-2]
        elif ret.endswith("._impl"):
            ret = ret[:-6]
        elif ret.endswith("_impl"):
            ret = ret[:-5]

        return ret

    @classmethod
    def shortname(cls) -> str:
        """
        Returns the shortname of the module name without _h or _impl suffixes.

        Shortname is only the last part of the name, without the package prefix.
        """
        return cls.basename().split(".")[-1]

    def __init_subclass__(cls, **kwargs) -> None:
        logger.debug(f"Module __init_subclass__ for: {cls.__name__}")
        super().__init_subclass__(**kwargs)

        ordered_attrs_to_resolve = [
            "name", "file", "description", "dependencies", 
            "authors", "changelog", "version", "fqn", "type", "role", "logger"
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
                
                if isinstance(original_descriptor_on_base, _ModuleBase.Attribute):
                    val_from_base_processor = original_descriptor_on_base.__get__(None, cls) # Call __get__ on the descriptor from _ModuleBase
                    
                    setattr(cls, attr_name, val_from_base_processor)
                    
            # Priority 2: Use the _ModuleBase.Attribute.resolve_for_class mechanism
            elif attr_name in _ModuleBase.__dict__:
                # Priority 2: If not always reprocessed, check for explicit concrete value on cls.
                val_explicitly_on_cls = cls.__dict__.get(attr_name)
                if val_explicitly_on_cls is not None and not isinstance(val_explicitly_on_cls, _ModuleBase.Attribute):
                    setattr(cls, attr_name, val_explicitly_on_cls)
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
    def cli(cls, *args, **kwargs):
        """
        Entry point for CLI interface. Here we start the App with the CLI mode and the current module as the CLI entry.
        """

        from pylium.core.app import App
        app = App()
        app.runCLI(App.RunMode.CLI, cls)

    @classmethod
    def list_submodules(cls) -> List[typing.Type["_ModuleBase"]]:
        """
        Return a list of all submodules of this module. 
        """

        file_dir = os.path.dirname(cls.file)
        if file_dir.endswith("__init__.py"):
            file_dir = os.path.dirname(file_dir)

        # We are a module, so find submodules with pkgutil
        print(f"shortname: {cls.basename()}")
        print(f"file_dir: {file_dir}")
        found_module_types: List[typing.Type["_ModuleBase"]] = []
        for submodule in pkgutil.iter_modules([file_dir]):
            
            # skip _impl.py and _version.py
            if submodule.name.endswith("_impl") or submodule.name.endswith("_version"):
                continue
            if submodule.name.startswith("_"):
                continue
            
            full_name = f"{cls.name}.{submodule.name}"
            logger.info(f"submodule: {full_name}")
            module = importlib.import_module(full_name)
            print(f"module: {module}")

            # Parse module for subclasses of _ModuleBase
            for attr_name in dir(module):
                try:
                    obj = getattr(module, attr_name)
                    # Check if it's a class and defined in this module
                    if isinstance(obj, type) and obj.__module__ == module.__name__:
                        print(f"Found locally defined class: {attr_name}")
                        if issubclass(obj, _ModuleBase):
                            logger.info(f"Found _ModuleBase subclass: {obj}")
                            found_module_types.append(obj)
                except Exception as e:
                    logger.warning(f"Error checking attribute {attr_name}: {e}")
                    continue

        return found_module_types

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
                    
                    if file_name.endswith("_impl.py") or file_name == "_version.py":
                        logger.debug(f"    list: Skipping impl or version file: '{os.path.join(subdir, file_name)}'")
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
                    
                    #logger.debug(f"    list: Attempting to import module: '{module_name_to_import}' from file '{full_file_path}'")
                    try:
                        module = importlib.import_module(module_name_to_import)
                        #logger.debug(f"      list: Successfully imported '{module_name_to_import}'")
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

        #logger.info(f"list: Completed scan for '{cls.__name__}'. Found {len(found_module_types)} matching module types: "
        #            f"{[t.__module__ + '.' + t.__name__ for t in found_module_types]}")
        return found_module_types

    @staticmethod
    def _get_current_os_info() -> Tuple[Optional[str], Optional[str]]:
        """
        Attempts to determine the current OS distribution and version.
        Reads /etc/os-release first, then falls back to /etc/issue.
        Returns:
            A tuple (distribution_name, distribution_version).
            Values can be None if detection fails.
        """
        distro_id: Optional[str] = None
        distro_version_id: Optional[str] = None

        # Try /etc/os-release first (standard for many modern distros)
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release", "r") as f:
                    os_release_vars = {}
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            # Remove quotes from value if present
                            if value.startswith(('"', "'")) and value.endswith(('"', "'")) and len(value) > 1:
                                value = value[1:-1]
                            os_release_vars[key.upper()] = value
                    
                    distro_id = os_release_vars.get("ID")
                    distro_version_id = os_release_vars.get("VERSION_ID")
                    logger.debug(f"_get_current_os_info: From /etc/os-release - ID='{distro_id}', VERSION_ID='{distro_version_id}'")
            except Exception as e:
                logger.warning(f"_get_current_os_info: Error reading /etc/os-release: {e}")
        
        # Fallback to /etc/issue if /etc/os-release didn't yield results
        if not distro_id or not distro_version_id:
            logger.debug(f"_get_current_os_info: /etc/os-release did not provide full info (ID: {distro_id}, Version: {distro_version_id}). Trying /etc/issue.")
            if os.path.exists("/etc/issue"):
                try:
                    with open("/etc/issue", "r") as f:
                        issue_content = f.readline().strip() # Usually first line is most relevant
                    logger.debug(f"_get_current_os_info: /etc/issue content (first line): '{issue_content}'")
                    
                    # Try to parse /etc/issue (this can be very distro-specific)
                    # Order of checks matters here.
                    if not distro_id: # If ID still missing
                        if re.search(r"ubuntu", issue_content, re.IGNORECASE):
                            distro_id = "ubuntu"
                        elif re.search(r"debian", issue_content, re.IGNORECASE):
                            distro_id = "debian"
                        elif re.search(r"fedora", issue_content, re.IGNORECASE):
                            distro_id = "fedora"
                        elif re.search(r"centos", issue_content, re.IGNORECASE):
                            distro_id = "centos"
                        elif re.search(r"alpine", issue_content, re.IGNORECASE):
                            distro_id = "alpine"
                        # Add more common distros as needed
                        else: # Try a generic grab
                            match_generic = re.match(r"([a-zA-Z]+)", issue_content)
                            if match_generic:
                                distro_id = match_generic.group(1).lower()
                    
                    if not distro_version_id: # If VERSION_ID still missing
                        # Common patterns: "Ubuntu 22.04.3 LTS", "Fedora release 38 (Thirty Eight)"
                        # "Debian GNU/Linux 12 (bookworm)", "Alpine Linux v3.18"
                        match_version = re.search(r"(\d+\.\d+(\.\d+)*)", issue_content) # Major.Minor.Patch(es)
                        if match_version:
                            distro_version_id = match_version.group(1)
                        else: # Try simpler \d+ for things like Fedora release 38
                            match_simple_version = re.search(r"(\d+)", issue_content)
                            if match_simple_version:
                                distro_version_id = match_simple_version.group(1)
                    logger.debug(f"_get_current_os_info: From /etc/issue (fallback) - Distro='{distro_id}', Version='{distro_version_id}'")

                except Exception as e:
                    logger.warning(f"_get_current_os_info: Error reading or parsing /etc/issue: {e}")
            else:
                logger.debug("_get_current_os_info: /etc/issue not found.")

        if distro_id:
            distro_id = distro_id.lower().strip()
        
        if distro_version_id:
            # For versions like "22.04.3 LTS", we often just want "22.04" for directory matching.
            # Take the first two components if it's a multi-part version.
            version_parts = distro_version_id.split('.')
            if len(version_parts) > 2:
                distro_version_id = f"{version_parts[0]}.{version_parts[1]}"
            elif len(version_parts) == 1: # e.g. "38" for Fedora
                 pass # Keep as is
            # If len is 2 e.g. "22.04" keep as is

        logger.debug(f"_get_current_os_info: Detected OS: {distro_id}, Version: {distro_version_id}")
        return distro_id, distro_version_id

    @classmethod
    def get_system_dependencies(cls, distribution_name: Optional[str] = None, 
                              distribution_version: Optional[str] = None) -> List[str]:
        """
        Retrieves a list of system-level package names required by this module's
        declared Pip dependencies for a specific OS distribution and version.

        If distribution_name or distribution_version are not provided, it attempts
        to detect them from the current operating system.

        Args:
            distribution_name (Optional[str]): The lowercase name of the OS distribution (e.g., 'ubuntu', 'fedora').
                                               If None, attempts to auto-detect.
            distribution_version (Optional[str]): The version string for the OS distribution (e.g., '22.04', '38').
                                                  If None, attempts to auto-detect.
        Returns:
            List[str]: A list of unique system package names.
        """
        detected_distro_name: Optional[str] = None
        detected_distro_version: Optional[str] = None

        if distribution_name is None or distribution_version is None:
            detected_distro_name, detected_distro_version = cls._get_current_os_info()

        final_distro_name = distribution_name if distribution_name is not None else detected_distro_name
        final_distro_version = distribution_version if distribution_version is not None else detected_distro_version

        if not final_distro_name or not final_distro_version:
            logger.warning(
                f"get_system_dependencies for {cls.__name__}: Could not determine OS distribution name or version. "
                f"(Provided: name='{distribution_name}', version='{distribution_version}'; "
                f"Detected: name='{detected_distro_name}', version='{detected_distro_version}'). "
                "Cannot look up system dependencies."
            )
            return []
        
        # Ensure these are strings for path joining and logging after checks
        final_distro_name_str = str(final_distro_name).lower().strip()
        final_distro_version_str = str(final_distro_version).strip()

        if not hasattr(cls, 'dependencies') or not isinstance(cls.dependencies, list):
            logger.debug(f"get_system_dependencies: Class {cls.__name__} has no 'dependencies' list or it's not a list. Returning empty.")
            return []

        all_sys_deps = set()
        
        if not os.path.isdir(_ModuleBase._pip2sysdep_data_path):
            logger.error(f"get_system_dependencies: Data directory not found at {_ModuleBase._pip2sysdep_data_path}. Cannot lookup system dependencies.")
            return []
        
        logger.debug(f"get_system_dependencies for {cls.__name__} on {final_distro_name_str} {final_distro_version_str}:")
        logger.debug(f"  Declared Pip dependencies: {[dep.name for dep in cls.dependencies if hasattr(dep, 'name')]}")

        for pip_dep in cls.dependencies:
            if not hasattr(pip_dep, 'name') or not isinstance(pip_dep.name, str):
                logger.warning(f"  Skipping invalid pip dependency object: {pip_dep}")
                continue
            
            pip_pkg_name = pip_dep.name.lower()
            
            found_for_pip_pkg = False
            path1_parts = [_ModuleBase._pip2sysdep_data_path, final_distro_name_str, final_distro_version_str, f"{pip_pkg_name}.txt"]
            path1 = os.path.join(*path1_parts)
            
            path2_parts = [_ModuleBase._pip2sysdep_data_path, final_distro_name_str, "_common_", f"{pip_pkg_name}.txt"]
            path2 = os.path.join(*path2_parts)

            paths_to_check = [path1, path2]
            current_sys_deps_for_pip_pkg = [] # Renamed to avoid confusion

            for dep_file_path in paths_to_check:
                if os.path.exists(dep_file_path) and os.path.isfile(dep_file_path):
                    logger.debug(f"    Found system dependency file for '{pip_pkg_name}': {dep_file_path}")
                    try:
                        with open(dep_file_path, 'r') as f:
                            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                            if lines:
                                current_sys_deps_for_pip_pkg.extend(lines)
                                found_for_pip_pkg = True 
                                break 
                    except Exception as e:
                        logger.error(f"    Error reading system dependency file {dep_file_path}: {e}")
                else:
                    #logger.debug(f"    System dependency file not found for '{pip_pkg_name}': {dep_file_path}")
                    pass
            
            if found_for_pip_pkg:
                all_sys_deps.update(current_sys_deps_for_pip_pkg)
                #logger.debug(f"      Added system deps for '{pip_pkg_name}': {current_sys_deps_for_pip_pkg}")
                pass
            else:
                #logger.debug(f"    No system dependency file found or file was empty for Pip package '{pip_pkg_name}' on {final_distro_name_str}/{final_distro_version_str} (checked {path1} and {path2})")
                pass

        final_list = sorted(list(all_sys_deps))
        #logger.debug(f"get_system_dependencies for {cls.__name__} on {final_distro_name_str} {final_distro_version_str}: Found {len(final_list)} system dependencies: {final_list}")
        return final_list

    @classmethod
    def get_implementation_module_class(cls) -> Optional[typing.Type["_ModuleBase"]]:
        """
        Returns the implementation module for this module.
        """

        possible_impl_modules = [cls.basename(), cls.basename() + "_impl", cls.basename() + "._impl"]

        for module_name in possible_impl_modules:
            logger.debug(f"get_implementation_module: Checking module {module_name}")
            try:
                mod = importlib.import_module(module_name)

                # Check if module contains a class that is a subclass of "_ModuleBase"
                tmp_mod_class = None
                if hasattr(mod, "__dict__"):
                    for name, obj in mod.__dict__.items():
                        if isinstance(obj, type) and issubclass(obj, _ModuleBase) and obj.__module__ == module_name:
                            if tmp_mod_class is None:
                                tmp_mod_class = obj
                            else:
                                logger.warning(f"get_implementation_module: Found multiple implementation classes for {cls.__name__} in {module_name}: {tmp_mod_class.__name__} and {obj.__name__}. Using first one.")

                if tmp_mod_class is not None:
                    from pylium.core.component import Component
                    # Check if there is a subclass of Component in the module "mod"
                    for name, obj in mod.__dict__.items():
                        if isinstance(obj, type) and issubclass(obj, Component):
                            # Check if is_impl is True
                            if hasattr(obj, "_is_impl") and obj._is_impl:
                                return tmp_mod_class
            except ImportError:
                pass

        logger.warning(f"Did not find implementation module class for {cls.__name__}")
        return None
        
        
