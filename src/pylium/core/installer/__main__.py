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
    txt = "Checking Python version ..."
    if sys.version_info < MIN_PYTHON_VERSION:
        logger.error(f"{txt} failed")
        logger.error(f" - ERROR: Python version {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher is required.")
        logger.error(f" - You are using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.")
        sys.exit(1)
    logger.info(f"{txt} passed (Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} >= {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]})")

def check_venv_module_available():
    """Checks for the venv module and exits with a hint if missing."""
    txt = "Checking for venv module ..."
    venv_spec = importlib.util.find_spec("venv")
    if venv_spec is None:
        logger.error(f"{txt} failed")
        logger.error(" - ERROR: Python 'venv' module is not installed or not found in the current Python environment.")
        logger.error(" - This module is required to create virtual environments.")
        logger.error(" - Please install it for your Python distribution.")
        
        system_platform = platform.system().lower()
        py_major = sys.version_info.major
        py_minor = sys.version_info.minor
        
        if system_platform == "linux":
            # Common package names, though actual package manager might vary (apt, yum, dnf, etc.)
            logger.info(f"  For Debian/Ubuntu, try: sudo apt-get install python{py_major}.{py_minor}-venv")
            logger.info(f"  For Fedora/CentOS/RHEL, try: sudo dnf install python{py_major}-virtualenv (or python{py_major}-venv)") 
        elif system_platform == "darwin": # macOS
            logger.info(f"  On macOS, python{py_major}.{py_minor} from python.org or Homebrew usually includes venv.")
            logger.info("  Ensure your Python installation is standard or consider reinstalling/upgrading.")
        elif system_platform == "windows":
            logger.info(f"  On Windows, the Python installer from python.org should include the venv module.")
            logger.info("  Ensure it was selected during installation or try repairing/reinstalling Python.")
        else:
            logger.info(f"  For your system ({system_platform}), please consult its documentation for installing the Python venv module.")
        
        sys.exit(1)
    logger.info(f"{txt} passed")

def create_or_confirm_venv(venv_path):
    """Creates a venv if it doesn't exist, or confirms it if it does."""
    venv_created = False
    txt = f"Creating virtual environment at: {venv_path}"
    if not os.path.exists(venv_path):
        logger.info(txt)
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
            logger.info("Virtual environment created successfully.")
            venv_created = True
        except subprocess.CalledProcessError as e:
            logger.error(f"ERROR: Failed to create virtual environment: {e}")
            sys.exit(1)
    else:
        # Basic check: is it a directory and does it have a python executable?
        python_in_venv = os.path.join(venv_path, "bin", "python") # Adjust for Windows if needed
        if os.path.isdir(venv_path) and os.path.exists(python_in_venv):
            logger.info(f"Virtual environment at {venv_path} already exists and seems valid.")
        else:
            logger.error(f"ERROR: Path {venv_path} exists but does not appear to be a valid virtual environment.")
            sys.exit(1)
    return os.path.abspath(venv_path), venv_created

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
            logger.error("ERROR: Editable install can only be used with a single string path for 'packages'.")
            sys.exit(1)
        install_command.append("-e")
    
    packages_to_display = ""

    if isinstance(packages, list):
        if editable:
            logger.error("ERROR: Cannot use editable=True with a list of packages.")
            sys.exit(1)
        if version_spec:
            logger.error("ERROR: Cannot use version_spec with a list of packages.")
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
        logger.error(f"ERROR: Invalid type for 'packages' argument: {type(packages)}")
        sys.exit(1)

    action = "Upgrading" if upgrade and not editable else "Installing"
    if editable: # Overrides action string if editable
        action = "Installing (editable)"
        
    target_venv_dir = os.path.dirname(os.path.dirname(venv_python_path))
    logger.debug(f"{action} {packages_to_display} into {target_venv_dir}...")
    logger.debug(f"Executing: {' '.join(install_command)}")
    try:
        process = subprocess.run(install_command, check=True, capture_output=True, text=True)
        logger.info(f"Successful {action.lower().split()[0]} of {packages_to_display}.") # e.g. Successfully installed/upgraded
        if process.stdout.strip():
            logger.debug("Output:\n%s", process.stdout)
        if process.stderr.strip():
            logger.error("Stderr:\n%s", process.stderr)
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR: Failed to {action.lower().split()[0]} {packages_to_display} into venv.")
        logger.error(f"Command: {' '.join(e.cmd)}")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error(f"ERROR: Could not find Python executable in venv: {venv_python_path}")
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


    check_python_version()
    check_venv_module_available()
    venv_abs_path, venv_created = create_or_confirm_venv(VENV_NAME)
    venv_python = os.path.join(venv_abs_path, "bin", "python") 
    logger.debug(f"Using venv: {venv_abs_path}")
    
    # venv was created, so we need to install the bootstrap packages
    # some libraries might be required very early like fire
    if venv_created:
        logger.debug("Installing bootstrap packages")
        install_package_into_venv(venv_python, BOOTSTRAP_PACKAGES, upgrade=True)

    # Go into venv and re-execute the installer
    # We have a venv check so parameters can be handed over 1:1
    exec_args = [venv_python, __file__] + sys.argv[1:]
    logger.debug(f"Re-executing with: {' '.join(exec_args)}")
    try:
        os.execv(venv_python, exec_args)
    except OSError as e:
        logger.error(f"ERROR: Failed to re-execute installer in venv: {e}")
        sys.exit(1)
    

    

def main_venv():
    logger.info(f"{Installer.__name__} @ {Installer._name()}^{Installer._version()}")

def main():
    # Determine if running inside a virtual environment created by this script or similar
    # This is the most reliable way within Python itself, regardless of how it was invoked.
    is_in_venv = (hasattr(sys, 'real_prefix') or \
                  (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

    if is_in_venv:
        logger.debug(f"Detected running inside a virtual environment (sys.prefix='{sys.prefix}', sys.base_prefix='{sys.base_prefix}').")
        main_venv()
    else:
        logger.debug(f"Detected running outside a virtual environment (sys.prefix='{sys.prefix}', sys.base_prefix='{sys.base_prefix}').")
        main_bootstrap()

    # The called function should handle exiting or re-executing.
    # If main_bootstrap re-executes successfully, code here isn't reached.
    # If main_venv finishes, or main_bootstrap fails to re-execute, we might reach here.
    # Explicit exit might be good practice depending on main_venv's final action.
    # exit(0) # Can be added if main_venv doesn't exit itself.

if __name__ == "__main__":
    main()
