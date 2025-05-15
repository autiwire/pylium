from ._h import *

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
    
logger = AppPackageImpl.logger

class AppImpl(App):
    """
    This class is the main entry point for the application.
    """

    _is_impl = True

    def run(self, run_mode: App.RunMode, cli_entry: Optional[Type[Module]|Type[Component]] = None):
        self._run_mode = run_mode
        self._cli_entry = cli_entry
        self._run()

    def _run(self):
        logger.debug(f"Running in {self._run_mode} mode")
        if self._run_mode == App.RunMode.CLI:
            from ._cli import CLI
            cli = CLI(self._cli_entry)
            cli._run()
        elif self._run_mode == App.RunMode.TASK:
            logger.debug(f"Task entry: {self._task_entry}")
            self._run_task()
        elif self._run_mode == App.RunMode.API:
            logger.debug(f"API entry: {self._api_entry}")
            self._run_api()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




    """



        # Get all components in this module
        from pylium.core.component import Component
        components = []        
        for name in dir(cls.__module__):
            obj = getattr(cls.__module__, name)
            if isinstance(obj, Component):
                components.append(obj)

        print(components)

        class CLI():
            def __init__(self, x=3, verbose=False):
                self.x = x
                self.verbose = verbose
                print("init")
                if self.verbose:
                    print("Verbose mode enabled.")
                # print(args) # Removed for clarity with fire flags
                # print(kwargs) # Removed for clarity with fire flags
                pass

            #def __call__(self, *args, **kwargs):
            #    pass

            def test(self):
                print("test")

            @classmethod
            def test2(cls):
                print("test2")

            class _SubCLI():
                def __init__(self, *args, **kwargs):
                    pass

                def test(self):
                    print("test")

            subcli = _SubCLI()
            SUBCLIX = _SubCLI
            
            # def SUBCLIY():
            #     return CLI._SubCLI()

        class CLI2(CLI):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def test3(self):
                print("test")

        import fire
        os.environ["PAGER"] = "cat"
        fire.Fire(CLI, name=cls.name)

    """

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


