from .__header__ import App, AppRunMode, Header, Component, Module
from .cli import AppCommandProvider
from .__cli_launcher_header__ import AppCliLauncherH
import logging

from pylium.core.package import Package
from typing import ClassVar, List, Optional, Type

logger = logging.getLogger(__name__)

class AppImpl(App):
    """
    This class is the main entry point for the application.
    """

    __class_type__ = Header.ClassType.Impl

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._run_mode = None
        self._cli_entry = None
        self._task_entry = None
        self._api_entry = None
        logger.debug("AppImpl initialized.")

    def run(self, run_mode: AppRunMode, cli_entry: Optional[Type[Module]|Type[Component]] = None, 
            task_entry=None, api_entry=None):
        self._run_mode = run_mode
        self._cli_entry = cli_entry
        self._task_entry = task_entry 
        self._api_entry = api_entry
        return self._execute_run_mode()

    def _execute_run_mode(self):
        logger.debug(f"AppImpl: Executing in {self._run_mode} mode")
        if self._run_mode == AppRunMode.CLI:
            if self._cli_entry is None:
                logger.warning("CLI mode selected but no cli_entry provided to AppImpl.run(). Using AppCommandProvider defaults.")
            
            command_provider = AppCommandProvider(cli_entry=self._cli_entry)
            logger.debug(f"AppImpl: Created AppCommandProvider for entry: {type(self._cli_entry).__name__ if self._cli_entry else 'None'}")

            cli_runner = AppCliLauncherH(command_component=command_provider)
            logger.debug("AppImpl: AppCliLauncherH instantiated.")

            try:
                logger.info("AppImpl: Launching CLI via AppCliLauncherH...")
                return cli_runner.launch()
            except Exception as e:
                logger.error(f"AppImpl: Error during CLI launch: {e}", exc_info=True)
                raise

        elif self._run_mode == AppRunMode.TASK:
            logger.debug(f"AppImpl: Task entry: {self._task_entry}")
            return self._run_task()
        elif self._run_mode == AppRunMode.API:
            logger.debug(f"AppImpl: API entry: {self._api_entry}")
            return self._run_api()
        else:
            logger.error(f"AppImpl: Unknown run mode: {self._run_mode}")
            raise ValueError(f"Unknown run mode: {self._run_mode}")

    def _run_task(self):
        logger.warning("AppImpl: _run_task() is not fully implemented.")
        return "Task execution placeholder result"

    def _run_api(self):
        logger.warning("AppImpl: _run_api() is not fully implemented.")
        return "API serving placeholder result"

#    apiClass: ClassVar[Optional[Type[Any]]] = _get_class_from_module("fastapi", FastAPI)
#    celeryClass: ClassVar[Optional[Type[Any]]] = _get_class_from_module("celery", Celery)
#    cliClass: ClassVar[Optional[Type[Any]]] = _get_class_from_module("fire", Fire)

#    @classmethod
#    def _get_class_from_module(cls, module_name: str, class_type: Type[Any]) -> Optional[Type[Any]]:
#        try:
#            from importlib import import_module
#            module = import_module(module_name)
#            return getattr(module, class_type.__name__)
#        except ImportError:
#            return None

#    @property
#    def api(self) -> Optional[Any]:
#        return self._api

#       @property
#    def celery(self) -> Optional[Any]:
#        return self._celery

#    @property
#    def cli(self) -> Optional[Any]:
#        return self._cli


#        self._api = self.apiClass() if self.apiClass else None
#        self._celery = self.celeryClass() if self.celeryClass else None
#        self._cli = self._cli_builder()

#    def _cli_builder(self) -> Any:
#        if self.cliClass:
#            return None
#        else:
#            return None


