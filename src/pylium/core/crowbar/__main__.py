"""
Entry point for the crowbar module.

Run with: python -m pylium.core.crowbar
"""

from pylium.core.app import App
from . import __manifest__

if __name__ == "__main__":
    App.default.run(frontend=App.Frontend.CLI, manifest=__manifest__) 