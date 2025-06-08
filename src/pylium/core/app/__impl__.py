from .__header__ import App, Header, Manifest
# from pylium.core.cli import CLI # This top-level import creates a cycle.

class AppImpl(App):
    """
    Implementation of the App class.
    """
    __class_type__ = Header.ClassType.Impl

    def run(self, manifest: "Manifest"):
        """
        Runs a component. For CLI frontends, it instantiates and
        starts the main CLI component.
        """

        print(f"Running app with manifest: {manifest}")
        print(f"Frontend: {manifest.frontend}")

        if manifest.frontend == self.Manifest.Frontend.CLI:
            from pylium.core.cli import CLI
            print(f"Running CLI with manifest: {manifest}")
            CLI(manifest=manifest).start()
        else:
            print(f"Running non-CLI component: {manifest.location.module}")