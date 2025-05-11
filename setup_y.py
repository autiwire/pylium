# setup.py
import pkgutil
import importlib
import os
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

def discover_dependencies(namespace="myproject"):
    deps = set()
    pkg = importlib.import_module(namespace)
    for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        try:
            hdr = importlib.import_module(f"{name}.__header__")
            for dep in getattr(hdr, "__dependencies__", []):
                deps.add(dep)
        except ModuleNotFoundError:
            continue
    return sorted(deps)

class PostInstallCommand(_install):
    """After installation: generate requirements.txt."""
    def run(self):
        _install.run(self)
        deps = discover_dependencies()
        req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
        with open(req_file, "w") as f:
            f.write("\n".join(deps))
        print(f"[info] requirements.txt written ({len(deps)} entries)")

# Main setup
setup(
    name             = "pylium",
    version          = "0.1.0",
    packages         = find_packages(where="src"),
    package_dir      = {"": "src"},
    install_requires = discover_dependencies(),
    cmdclass         = {
        'install': PostInstallCommand,
    },
    include_package_data = True,
)