# src/pylium/__init__.py
try:
    from ._version import version as __version__
except ImportError:
    # This is a fallback for cases where the package is not installed
    # or _version.py has not been generated (e.g., a raw source checkout).
    __version__ = "0.0.0.unknown" # Or some other placeholder

# Optionally, expose key public APIs from pylium's submodules here for easier access
# For example:
# from .core.module import Module
# from .core.package import Package
# from .core.project import Project
# from .core.installer import InstallerPackage 