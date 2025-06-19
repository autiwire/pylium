from .__header__ import App, Header, Manifest
from pylium.core.frontend import Frontend

from typing import Type
import sys


class AppImpl(App):
    """
    Implementation of the App class.
    """
    __class_type__ = Header.ClassType.Impl


    @Manifest.func(App.test.__manifest__)
    def test(self):
        print("test_impl")
        print(f"Manifest: {self.__manifest__}")


    @classmethod
    @Manifest.func(App.test2.__manifest__)
    def test2(cls):
        print("test2_impl")
        print(f"Manifest: {cls.__manifest__}")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def run(self, frontend: Type[App.Frontend], manifest: Manifest):
        """
        Runs a component. For CLI frontends, it instantiates and
        starts the main CLI component.
        """

        from pylium.core.cli import CLI

#        print(f"Running app with manifest: {manifest}")
#        print(f"Frontend in app: {frontend.name}")
#        print(f"Frontend in manifest: {manifest.frontend.name}")

        if not frontend or not frontend in manifest.frontend:
            print(f"Error: Component {manifest.location.fqnShort} is not enabled for frontend {frontend.name}")
            print(f"Available frontends: {[f.name for f in manifest.frontend]}")
            print(f"To use this component, you need to:")
            print(f"  Enable {frontend.name} in {manifest.location.fqnShort} manifest")
            sys.exit(1)

#        print(f"Frontend type: {frontend.name}")
        frontend_class = Frontend.getFrontend(frontend)
#        print(f"Frontend class: {frontend_class}")
        if frontend_class is None:
            print(f"Error: No frontend class found for {frontend.name}")
            sys.exit(1)
        
        self.frontend = frontend_class(manifest=manifest)
        ret = self.frontend.start()
        if ret is False:
            print(f"Error: Failed to start frontend {frontend.name}")
            sys.exit(1)

        sys.exit(0)

    
