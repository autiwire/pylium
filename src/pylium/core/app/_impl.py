from ._h import App
from pylium.core.package import Package

from typing import Any, Optional, ClassVar, Type, List


class AppPackageImpl(Package):
    """
    This Package contains the core functionality of the application.
    """
    authors: ClassVar[List[Package.AuthorInfo]] = [
        Package.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Package.Date(2025, 5, 15))
    ]
    changelog: ClassVar[List[Package.ChangelogEntry]] = [
        Package.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Package.Date(2025, 5, 15)),
    ]
    


class AppImpl(App):
    """
    This class is the main entry point for the application.
    """

    _is_impl = True

    def run(self, run_mode: App.RunMode):
        self._run_mode = run_mode
        self._run()

    def _run(self):
        print(f"Running in {self._run_mode} mode")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




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


