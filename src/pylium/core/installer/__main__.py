from pylium.core.installer import Installer

import sys
import os
import subprocess
import importlib.util
import platform
import argparse
from typing import Optional, Union, List

import logging
# set loglevel to DEBUG
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MIN_PYTHON_VERSION = (3, 10)
BOOTSTRAP_PACKAGES = ["pip", "setuptools", "wheel", "fire"]
VENV_NAME = ".venv"

def check_python_version():
    """Checks if the current Python version meets the minimum requirement."""
    if sys.version_info < MIN_PYTHON_VERSION:
        print(f"ERROR: Python version {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher is required.")
        print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.")
        sys.exit(1)
    print(f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} is sufficient.")

def ensure_venv_module_available():
    """Checks for the venv module and exits with a hint if missing."""
    venv_spec = importlib.util.find_spec("venv")
    if venv_spec is None:
        print("ERROR: Python 'venv' module is not installed or not found in the current Python environment.")
        print("This module is required to create virtual environments.")
        print("Please install it for your Python distribution.")
        
        system_platform = platform.system().lower()
        py_major = sys.version_info.major
        py_minor = sys.version_info.minor
        
        if system_platform == "linux":
            # Common package names, though actual package manager might vary (apt, yum, dnf, etc.)
            print(f"  For Debian/Ubuntu, try: sudo apt-get install python{py_major}.{py_minor}-venv")
            print(f"  For Fedora/CentOS/RHEL, try: sudo dnf install python{py_major}-virtualenv (or python{py_major}-venv)") 
        elif system_platform == "darwin": # macOS
            print(f"  On macOS, python{py_major}.{py_minor} from python.org or Homebrew usually includes venv.")
            print("  Ensure your Python installation is standard or consider reinstalling/upgrading.")
        elif system_platform == "windows":
            print(f"  On Windows, the Python installer from python.org should include the venv module.")
            print("  Ensure it was selected during installation or try repairing/reinstalling Python.")
        else:
            print(f"  For your system ({system_platform}), please consult its documentation for installing the Python venv module.")
        
        sys.exit(1)
    print("Python 'venv' module is available.")

def create_or_confirm_venv(venv_path):
    """Creates a venv if it doesn't exist, or confirms it if it does."""
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at: {venv_path}")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
            print("Virtual environment created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to create virtual environment: {e}")
            sys.exit(1)
    else:
        # Basic check: is it a directory and does it have a python executable?
        python_in_venv = os.path.join(venv_path, "bin", "python") # Adjust for Windows if needed
        if os.path.isdir(venv_path) and os.path.exists(python_in_venv):
            print(f"Virtual environment at {venv_path} already exists and seems valid.")
        else:
            print(f"ERROR: Path {venv_path} exists but does not appear to be a valid virtual environment.")
            sys.exit(1)
    return os.path.abspath(venv_path)

def install_package_into_venv(
    venv_python_path: str, 
    packages: Union[str, List[str]], 
    editable: bool = False, 
    version_spec: Optional[str] = None, 
    upgrade: bool = False
):
    """Installs or upgrades package(s) into the specified virtual environment using pip.

    Args:
        venv_python_path: Path to the Python executable in the virtual environment.
        packages: A single package name/path (str) or a list of package names (List[str]).
        editable: If True, install in editable mode (applies if 'packages' is a str path).
        version_spec: Version specifier (applies if 'packages' is a single str package name).
        upgrade: If True, use 'pip install --upgrade'.
    """
    
    install_command = [venv_python_path, "-m", "pip", "install"]
    
    if upgrade:
        install_command.append("--upgrade")
    
    if editable:
        if not isinstance(packages, str):
            print("ERROR: Editable install can only be used with a single string path for 'packages'.")
            sys.exit(1)
        install_command.append("-e")
    
    packages_to_display = ""

    if isinstance(packages, list):
        if editable:
            print("ERROR: Cannot use editable=True with a list of packages.")
            sys.exit(1)
        if version_spec:
            print("ERROR: Cannot use version_spec with a list of packages.")
            sys.exit(1)
        install_command.extend(packages)
        packages_to_display = " ".join(packages)
    elif isinstance(packages, str):
        package_name_for_install = packages
        if version_spec and not editable: # version_spec not typically used with -e .
            package_name_for_install = f"{packages}{version_spec}"
        install_command.append(package_name_for_install)
        packages_to_display = package_name_for_install
    else:
        print(f"ERROR: Invalid type for 'packages' argument: {type(packages)}")
        sys.exit(1)

    action = "Upgrading" if upgrade and not editable else "Installing"
    if editable: # Overrides action string if editable
        action = "Installing (editable)"
        
    target_venv_dir = os.path.dirname(os.path.dirname(venv_python_path))
    print(f"{action} {packages_to_display} into {target_venv_dir}...")
    print(f"Executing: {' '.join(install_command)}")
    try:
        process = subprocess.run(install_command, check=True, capture_output=True, text=True)
        print(f"Successfully {action.lower().split()[0]}ed {packages_to_display}.") # e.g. Successfully installed/upgraded
        if process.stdout.strip():
            print("Output:\\n", process.stdout)
        if process.stderr.strip():
            print("Stderr:\\n", process.stderr)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to {action.lower().split()[0]} {packages_to_display} into venv.")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: Could not find Python executable in venv: {venv_python_path}")
        sys.exit(1)

class InstallerCommands:
    """Defines commands for the Pylium installer, to be exposed via Fire CLI."""

    def install(self, module_name: str):
        """
        Finds a Pylium module by its name or FQN and lists its details and system dependencies.

        Args:
            module_name: The name or fully qualified name of the Pylium module.
        """
        print(f"--- Pylium Installer: Install Command --- ")
        print(f"Attempting to find module: {module_name}")

        try:
            from pylium.core.module import Module
            print(f"Using Pylium Module system from: {Module.__module__}")
        except ImportError as e:
            print(f"CRITICAL ERROR: Pylium Module system (pylium.core.module.Module) could not be imported: {e}")
            print("This indicates a problem with the Pylium installation in the virtual environment.")
            sys.exit(1)

        found_module_class = None
        available_modules = Module.list()
        
        if not available_modules:
            print("No Pylium modules found by Module.list(). Ensure modules are defined and discoverable.")
        else:
            print(f"Available modules found: {[m.fqn for m in available_modules]}")


        for mod_class in available_modules:
            if mod_class.fqn == module_name or mod_class.__name__ == module_name:
                found_module_class = mod_class
                break
        
        if found_module_class:
            print(f"\nSuccessfully found module: {found_module_class.fqn} (Class: {found_module_class.__name__})")
            print(f"  Name:         {getattr(found_module_class, 'name', 'N/A')}")
            print(f"  Version:      {getattr(found_module_class, 'version', 'N/A')}")
            print(f"  Description:  {getattr(found_module_class, 'description', 'N/A')}")
            
            authors_list = getattr(found_module_class, 'authors', [])
            if authors_list:
                print(f"  Authors:      {', '.join(str(a) for a in authors_list)}")
            else:
                print("  Authors:      N/A")

            try:
                system_dependencies = found_module_class.get_system_dependencies()
                if system_dependencies:
                    print("  System Dependencies (OS-specific packages):")
                    for os_type, packages in system_dependencies.items():
                        if packages:
                            print(f"    {os_type}: {', '.join(packages)}")
                        else:
                            print(f"    {os_type}: None specified")
                else:
                    print("  System Dependencies: None defined for this module.")
            except Exception as e:
                print(f"  Error retrieving system dependencies: {e}")
            
            # Placeholder for actual installation steps
            print("\nTODO: Implement actual installation of system and pip dependencies.")

        else:
            print(f"\nERROR: Module '{module_name}' not found among available Pylium modules.")
            print(f"Searched in: {[m.fqn for m in available_modules]}")
            sys.exit(1)
        
        print(f"--- Module {module_name} processing complete --- ")

def main_bootstrap():
    logger.debug("Starting Bootstrap")

    logger.debug("Checking Python version")
    check_python_version()

    logger.debug("Ensuring venv module is available")
    ensure_venv_module_available()
    
    logger.debug("Creating venv")
    venv_abs_path = create_or_confirm_venv(VENV_NAME)
    venv_python = os.path.join(venv_abs_path, "bin", "python") 
    logger.debug(f"Using virtual environment python: {venv_python}")
    
    logger.debug("Installing bootstrap packages")
    install_package_into_venv(venv_python, BOOTSTRAP_PACKAGES, upgrade=True)

    #logger.debug("Installing Pylium")
    #install_package_into_venv(venv_python, ".", editable=True)
    
    
    

def main_venv():
    logger.info(f"{Installer.__name__} @ {Installer._name()}^{Installer._version()}")

def main():    
    #running_in_virtualenv = "VIRTUAL_ENV" in os.environ
    running_in_virtualenv = False # TODO: Remove this
    if running_in_virtualenv:
        main_venv()
    else:
        main_bootstrap()

    exit(0)

    args, remaining_argv = parser.parse_known_args() # Use parse_known_args if we expect Fire to parse later

    if not args.running_in_venv:
        print("--- Pylium Installer: Starting Bootstrap (Phase 1) ---")
        check_python_version()
        ensure_venv_module_available()
        
        venv_abs_path = create_or_confirm_venv(VENV_NAME)
        venv_python = os.path.join(venv_abs_path, "bin", "python") 
        print(f"Using virtual environment python: {venv_python}")
        
        # 1. Install/Upgrade all bootstrap packages in one go
        print("--- Ensuring all bootstrap packages are installed/upgraded ---")
        install_package_into_venv(venv_python, BOOTSTRAP_PACKAGES, upgrade=True)
        
        print("--- Installing Pylium into the virtual environment ---")
        install_package_into_venv(venv_python, ".", editable=True)
        
        print("--- Pylium bootstrapped into venv. Re-executing installer inside the venv... ---")
        
        # Prepare arguments for re-execution
        # The first argument to execv is the path to the new program to execute.
        # The second argument is a list of strings, where the first string is conventionally the program name itself.
        new_process_args = [venv_python, __file__, "--running-in-venv"] + remaining_argv + sys.argv[1:]
        # Filter out the old --running-in-venv if it somehow got passed in the first run's sys.argv
        # and also filter out the initial call to the script if it was `python -m pylium.core.installer ...`
        # This part can be tricky to get perfectly robust for all invocation methods.
        # A simpler approach might be to just pass specific known installer args.
        
        # For a cleaner re-exec, ensure __file__ is the script path, not -m module path
        script_path = os.path.abspath(__file__)
        
        # Re-construct arguments for the new process
        # venv_python, script_path itself, --running-in-venv, then other args
        # This assumes other installer CLI commands will be defined on the parser for the venv phase
        exec_args = [venv_python, script_path, "--running-in-venv"] + sys.argv[1:]
        # A common issue: if first call was `python -m module`, sys.argv[0] is the full path to __main__.py
        # if it was `python path/to/__main__.py`, sys.argv[0] is `path/to/__main__.py`
        # os.execv needs the first arg in `exec_args` to be the program name for argv[0] of the new process

        print(f"Re-executing with: {' '.join(exec_args)}")
        try:
            os.execv(venv_python, exec_args)
        except OSError as e:
            print(f"ERROR: Failed to re-execute installer in venv: {e}")
            sys.exit(1)
        # os.execv replaces the current process, so code here won't run if successful

    else:
        print("--- Pylium Installer: Running Inside Venv (Phase 2) ---")

        # Sanity check: Verify we are actually running from a virtual environment's Python
        # This complements the --running-in-venv flag.
        is_in_venv = (hasattr(sys, 'real_prefix') or \
                      (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
        
        if not is_in_venv:
            print("CRITICAL WARNING: Installer indicates Phase 2 (in-venv) but sys.prefix/sys.base_prefix suggest otherwise!")
            print(f"  sys.prefix: {sys.prefix}")
            if hasattr(sys, 'base_prefix'):
                print(f"  sys.base_prefix: {sys.base_prefix}")
            if hasattr(sys, 'real_prefix'): # For older virtualenv versions
                print(f"  sys.real_prefix: {getattr(sys, 'real_prefix')}")
            print("This could indicate an issue with the re-execution logic or the environment.")
            # Consider exiting if this fundamental assumption is violated.
            # sys.exit(1) 
        else:
            print(f"Confirmed running in a virtual environment (sys.prefix: {sys.prefix}).")

        # Ensure src directory is prioritized for imports in Phase 2
        installer_script_dir = os.path.dirname(os.path.abspath(__file__))
        project_src_dir = os.path.abspath(os.path.join(installer_script_dir, '..', '..', '..'))
        
        if project_src_dir not in sys.path:
            sys.path.insert(0, project_src_dir)
        
        try:
            import pylium # For version
            from pylium.core.module import Module 
            print(f"Successfully imported Pylium version {pylium.__version__} from venv.")
        except ImportError as e:
            print(f"ERROR: Failed to import Pylium from within the venv, even after re-execution: {e}")
            print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
            print(f"sys.path: {sys.path}")
            sys.exit(1)

        print("--- Pylium (from venv) is now active. Initializing CLI... ---")
        
        import fire # Import Fire for Phase 2 CLI
        # Pass remaining_argv to Fire. If empty, Fire shows help. 
        # If it contains commands, Fire dispatches them.
        fire.Fire(InstallerCommands, command=remaining_argv if remaining_argv else None)

if __name__ == "__main__":
    main()
