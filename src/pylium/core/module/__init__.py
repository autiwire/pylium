from typing import List, ClassVar, Optional, Any, Callable
from enum import Enum
from abc import ABC, abstractmethod, ABCMeta
import dataclasses
import os
import sys
import datetime

import logging
logger = logging.getLogger(__name__)

from ._base import _ModuleBase

class Module(_ModuleBase):
    """
    A module represented by a single Python (.py) file.
    """
    type: ClassVar[_ModuleBase.Type] = _ModuleBase.Type.MODULE
    authors: ClassVar[List[_ModuleBase.AuthorInfo]] = [
        _ModuleBase.AuthorInfo(name="Rouven Raudzus", email="raudzus@autiwire.org", since_version="0.0.1", since_date=datetime.date(2025, 5, 10))
    ]
    changelog: ClassVar[List[_ModuleBase.ChangelogEntry]] = [
        _ModuleBase.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=datetime.date(2025, 5, 10))
    ]
    dependencies: ClassVar[List[_ModuleBase.Dependency]] = [
        _ModuleBase.Dependency(name="pydantic", type=_ModuleBase.Dependency.Type.PIP, version="2.10.2"),
        _ModuleBase.Dependency(name="fire", type=_ModuleBase.Dependency.Type.PIP, version="0.5.0"),
    ]

    @classmethod
    def cli(cls, *args, **kwargs):
        """
        Entry point for CLI interface.

        Here we dynamically create a CLI interface class for the module.

        The interface is used to invoke the module's functionality, which 
        itself is defined in "components" of the module. A module has to detect 
        what kind of module it is (Bundle, Header, Implementation) and then
        build the appropriate CLI interface from the components.

        Bundle:
         - Search for Component classes in this module and header module
         - Create a CLI interface class that bundles the components

        Header:
         - Search for Component classes in this module
         - Create a CLI interface that delivers information about the module

        Implementation:
         - Search for Component classes in this module
         - Create a CLI interface that delivers information about the implementation

        CLI commands should be always invoked over a bundle, e.g.
        for python3 -m pylium.core.example it should be a Bundle defined in 
        pylium/core/example/__init__.py or pylium/core/example.py.

        Scan bundle and - if existing - header module for Component classes.
        

        
        """

        # TEST
        from pylium.core.app import App
        app = App()
        app.run(App.RunMode.CLI)


        return

        


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

__all__ = ["Module"]