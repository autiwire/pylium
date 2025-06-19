"""
Manifest Discovery with pkgutil instead of importlib

This shows how to use pkgutil for more efficient module discovery
without loading modules unnecessarily.
"""

import pkgutil
import importlib
import inspect
from typing import List, Optional

class ManifestDiscovery:
    """
    Efficient manifest discovery using pkgutil for module discovery
    and importlib only when needed.
    """
    
    def discover_children(self, location) -> List:
        """Discover manifest children using pkgutil."""
        childs = []
        
        try:
            # Use pkgutil to discover modules without loading them
            module_found = False
            discovered_module = None
            
            # Search in all available paths
            for finder, name, ispkg in pkgutil.iter_modules():
                if name == location.shortName:
                    module_found = True
                    discovered_module = name
                    break
            
            if not module_found:
                # Also check packages
                for finder, name, ispkg in pkgutil.iter_modules():
                    if ispkg and name == location.shortName:
                        module_found = True
                        discovered_module = name
                        break
            
            if module_found:
                # Only load the module when we need it
                module = importlib.import_module(discovered_module)
                print(f"  MODULE: {module}")
                
                # Now process the loaded module
                childs = self._process_module_children(module, location, childs)
            else:
                print(f"  MODULE NOT FOUND: {location.shortName}")
                
        except Exception as e:
            print(f"  ERROR discovering module {location.shortName}: {e}")
        
        return childs
    
    def _process_module_children(self, module, location, childs: List) -> List:
        """Process children of a loaded module."""
        
        if location.isModule and location.isPackage:
            # Process package/module children
            for name, member in inspect.getmembers(module):
                if name.startswith("__") and name.endswith("__"):
                    continue
                
                if hasattr(member, "__manifest__"):
                    if member.__manifest__.parent == location and member.__manifest__ not in childs:
                        print(f"ADD_MOD: {member.__manifest__.location.fqnShort}")
                        childs.append(member.__manifest__)
        
        elif location.isClass:
            # Process class children
            my_class = getattr(module, location.classname)
            if hasattr(my_class, "__manifest__"):
                for name, member in inspect.getmembers(my_class):
                    if name.startswith("__") and name.endswith("__"):
                        continue
                    
                    if hasattr(member, "__manifest__"):
                        if member.__manifest__.parent == location and member.__manifest__ not in childs:
                            print(f"ADD_CLASS: {member.__manifest__.location.fqnShort}")
                            childs.append(member.__manifest__)
        
        elif location.isFunction:
            # Functions don't have children
            pass
        
        return childs
    
    def discover_all_modules(self) -> List[str]:
        """Discover all available modules using pkgutil."""
        modules = []
        
        for finder, name, ispkg in pkgutil.iter_modules():
            modules.append({
                'name': name,
                'is_package': ispkg,
                'finder': finder
            })
        
        return modules
    
    def discover_package_modules(self, package_name: str) -> List[str]:
        """Discover all modules in a specific package."""
        modules = []
        
        try:
            package = importlib.import_module(package_name)
            
            for finder, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                modules.append({
                    'name': name,
                    'is_package': ispkg,
                    'finder': finder
                })
        except ImportError:
            print(f"Package {package_name} not found")
        
        return modules

# Example usage
if __name__ == "__main__":
    discovery = ManifestDiscovery()
    
    # Discover all modules
    print("=== All Available Modules ===")
    all_modules = discovery.discover_all_modules()
    for module in all_modules[:10]:  # Show first 10
        print(f"  {module['name']} {'(package)' if module['is_package'] else '(module)'}")
    
    # Discover package modules
    print("\n=== Pylium Package Modules ===")
    pylium_modules = discovery.discover_package_modules('pylium')
    for module in pylium_modules:
        print(f"  {module['name']} {'(package)' if module['is_package'] else '(module)'}") 