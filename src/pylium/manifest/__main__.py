"""
This is a generic, copyable main entry point for a Pylium module.

To make any module runnable, copy this file into its package directory.
It automatically finds the central default App instance and tells it to
run this module based on the module's own __manifest__.
"""

from . import __manifest__
from pylium.core.app import App

#print(f"XXX __manifest__@pylium/manifest/__main__.py: {__manifest__}")
#print(f"XXX __manifest__@pylium/manifest/__main__.py: parent: {__manifest__.parent}")
#print(f"XXX __manifest__@pylium/manifest/__main__.py: children: {__manifest__.children}")


if __name__ == "__main__":
    App.default.run(manifest=__manifest__)


