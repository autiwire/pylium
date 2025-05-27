from .__header__ import App, AppRunMode # Assuming _h defines these, or adjust as needed
from pylium.core.module import Module
from pylium.core.component import Component # Assuming these are the base types for cli_entry

from typing import ClassVar, List, Optional, Type
import os
# import pkgutil # pkgutil might not be needed if Module.list_submodules() is sufficient

# It seems CLIModule was old metadata, AppCommandProvider will be the main focus.
# class CLIModule(Module): ... (keeping if used, removing if not)

# Assuming Module.logger or a new logger for this file
import logging
logger = logging.getLogger(__name__) # Or Module.logger if CLIModule was kept and had it

class AppCommandProvider(): # Renamed from CLI
    """
    Builds a command structure for python-fire based on a Pylium Module or Component.
    This class itself becomes the command component for fire.Fire().
    """
    def __init__(self, cli_entry: Optional[Type[Module]|Type[Component]] = None, 
                 cli_name: Optional[str] = None, 
                 # cli_pager: Optional[str] = "cat", # Pager is handled by fire.Fire, not here
                 *args, **kwargs):
        # super().__init__(*args, **kwargs) # No clear superclass that requires this now
        self._cli_entry = cli_entry
        self._cli_name = cli_name # This might be useful for fire.Fire(self, name=self._cli_name)
                                    # but PyliumCliH doesn't use it yet. We can pass it to PyliumCliH 
                                    # if we enhance PyliumCliH to accept a top-level name.

        if self._cli_entry:
            # Determine a default name if not provided
            if not self._cli_name and hasattr(self._cli_entry, 'name'):
                self._cli_name = self._cli_entry.name 

            if issubclass(self._cli_entry, Module):
                self._init_module_cli()
            elif issubclass(self._cli_entry, Component):
                self._init_component_cli()
            else:
                # Allow cli_entry to be None, in which case this provider might offer default commands
                if self._cli_entry is not None:
                    raise ValueError(f"Invalid CLI entry type: {self._cli_entry}")
        else:
            logger.debug("AppCommandProvider initialized without a specific cli_entry. It may offer default commands or be empty.")

    def _init_module_cli(self):
        logger.debug(f"Initializing AppCommandProvider for Module: {self._cli_entry.__name__}")
        # Example: Add some methods from the module itself, or sub-commands
        # This replicates the logic for adding submodules as commands.
        # Ensure that `list_submodules` and `shortname` are valid methods/attributes of your Module class.
        if hasattr(self._cli_entry, 'list_submodules'):
            for submodule_info in self._cli_entry.list_submodules(): # Assuming this returns usable info
                # Adapt this logic based on what list_submodules returns and how Module.Role is defined
                # For example, if submodule_info is the module class itself:
                submodule_class = submodule_info # Placeholder, adjust based on actual return type
                if hasattr(submodule_class, 'role') and submodule_class.role == Module.Role.BUNDLE:
                    # The attribute name should be python-identifier friendly
                    # The name for fire can be handled by fire itself (e.g. from method/class name)
                    attr_name = submodule_class.shortname() # Assuming shortname() gives a good python id
                    sub_provider_name = submodule_class.basename() if hasattr(submodule_class, 'basename') else attr_name
                    setattr(self, attr_name, AppCommandProvider(submodule_class, cli_name=sub_provider_name))
                    logger.debug(f"  Added submodule {attr_name} as a command group.")
        else:
            logger.warning(f"Module {self._cli_entry.__name__} does not have 'list_submodules' method. Cannot auto-add sub-commands.")
        
        # You might want to add some default commands or expose module methods here
        # e.g. self.info = lambda: print(f"Info about {self._cli_entry.name}")

    def _init_component_cli(self):
        logger.debug(f"Initializing AppCommandProvider for Component: {self._cli_entry.__name__}")
        # For components, you might want to inspect its methods and add them as commands
        # Or, if components have a specific structure for defining CLI commands, use that.
        # This part needs to be filled based on how your Components define their CLI surface.
        # For now, it's a placeholder.
        logger.info(f"  Component CLI initialization for {self._cli_entry.__name__} is placeholder.")
        # Example: self.component_action = self._cli_entry.some_action_method

    # The _run method is removed, as PyliumCliH will call fire.Fire()
    # def _run(self):
    #     import fire
    #     os.environ["PAGER"] = self._cli_pager # PAGER is set by fire or user env
    #     fire.Fire(self,name=self._cli_name)

    # Add any default commands AppCommandProvider might offer if cli_entry is None
    def provider_info(self):
        """Displays information about this command provider."""
        entry_name = self._cli_entry.__name__ if self._cli_entry else "None"
        return f"AppCommandProvider for cli_entry: {entry_name}. Name: {self._cli_name or 'Default'}"

# Keep CLIModule if it's used elsewhere, or remove if it was just for the old CLI class.
# For now, I'll assume it might be part of the Module structure and leave its definition commented out or minimal.
# class CLIModule(Module):
# authors: ...
# changelog: ...
# logger = CLIModule.logger
