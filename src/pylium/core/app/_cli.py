from ._h import *

import os
import pkgutil

class CLIModule(Module):
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=Module.Date(2025, 5, 15))
    ]
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=Module.Date(2025, 5, 15))
    ]

logger = CLIModule.logger

class CLI():
    def __init__(self, cli_entry: Optional[Type[Module]|Type[Component]] = None, cli_name: Optional[str] = None, cli_pager: Optional[str] = "cat", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cli_entry = cli_entry
        self._cli_name = cli_name
        self._cli_pager = cli_pager

        if self._cli_entry:
            if issubclass(self._cli_entry, Module):
                self._init_module_cli()
            elif issubclass(self._cli_entry, Component):
                self._init_component_cli()
            else:
                raise ValueError(f"Invalid CLI entry type: {self._cli_entry}")

    def _init_module_cli(self):
        def test():
            print(f"Module: {self._cli_entry}")

        self.test = test
        self.test2 = test
        self._cli_name = self._cli_entry.name
        
        # We are a module, so find submodules with pkgutil

        logger.info(f"XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    
        for submodule in self._cli_entry.list_submodules():            
            logger.info(f"Submodule: {submodule}")

            # Only add submodules which are a bundle
            if submodule.role == Module.Role.BUNDLE:
                setattr(self, submodule.shortname(), CLI(submodule, submodule.basename()))
    
        logger.info(f"XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        


    def _init_component_cli(self):
        pass

    def _run(self):
        import fire
        os.environ["PAGER"] = self._cli_pager
        fire.Fire(self,name=self._cli_name)
