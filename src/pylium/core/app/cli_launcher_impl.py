import fire
from typing import Any, Optional, Sequence

from .cli_launcher_h import AppCliLauncherH # Updated import
from pylium.core.header import Header # For Header.ClassType

import logging
logger = logging.getLogger(__name__)

class AppCliLauncherI(AppCliLauncherH):
    __class_type__ = Header.ClassType.Impl

    def __init__(self, command_component: Optional[Any] = None, **kwargs):
        super().__init__(command_component=command_component, **kwargs)
        self._command_component = command_component
        logger.debug(f"AppCliLauncherI initialized. Command component type: {type(self._command_component).__name__}")

    def launch(self, *cli_args: str) -> Any:
        target_component = self._command_component if self._command_component is not None else self
        
        logger.info(f"Launching App CLI with fire. Target: {type(target_component).__name__}. Args: {cli_args if cli_args else 'sys.argv'}")
        
        if cli_args:
            return fire.Fire(target_component, command=list(cli_args))
        else:
            return fire.Fire(target_component)

    def default_command(self, message="App CLI Launcher Impl default command executed!"):
        logger.info(f"AppCliLauncherI.default_command called: {message}")
        return message 