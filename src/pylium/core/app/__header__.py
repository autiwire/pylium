from pylium.core.header import Header, Manifest
from pylium.core.module import Module
# from pylium.core.component import Component

from typing import ClassVar, List, Optional, Type
import enum

class AppRunMode(enum.Enum):
    CLI = "cli"
    API = "api"
    TASK = "task"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value

class App(Header):
    """
    This class is the main entry point for the application.
    It manages different run modes like CLI, API, and Tasks.
    """
    manifest = Manifest(
        name="Pylium Core Application",
        description="Core application component capable of running in CLI, API, or Task mode.",
        authors=[
            {"name": "Rouven Raudzus", "email": "raudzus@autiwire.org"}
        ],
        changelog=[
            {"version": "0.0.1", "notes": ["Initial release"], "date": "2025-05-15"}
        ],
        dependencies=[
            "pydantic==2.10.2", 
            "fire==0.5.0", 
            "fastapi==0.105.1", 
            "uvicorn==0.25.0"
        ],
        location=__file__
    )
    __class_type__ = Header.ClassType.Header

    RunMode = AppRunMode

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, run_mode: AppRunMode, cli_entry: Optional[Type[Module]|Type[Component]] = None, task_entry=None, api_entry=None):
        """
        Executes the application in the specified mode.
        Implementation is in AppImpl.

        Args:
            run_mode: The mode to run the application in (CLI, API, TASK).
            cli_entry: The entry point for CLI mode (Module or Component type).
            task_entry: The entry point or configuration for TASK mode.
            api_entry: The entry point or configuration for API mode.
        """
        if type(self) == App: # pragma: no cover
             raise NotImplementedError(
                "App.run() called directly on Header. "
                "This method should be executed on an AppImpl instance."
            )
        pass


