from pylium.core import __manifest__ as __parent__
from pylium.manifest import Manifest
from pylium.core.header import Header, classProperty, dlock

import threading
from abc import abstractmethod
from typing import Type, Optional, Dict, List
import packaging.version

__manifest__ : Manifest = __parent__.createChild(
    location=Manifest.Location(module=__name__, classname=None), 
    description="Installer and package management system for Pylium",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    dependencies=[
        Manifest.Dependency(name="pip", version="25.3.0", type=Manifest.Dependency.Type.PIP,
                          category=Manifest.Dependency.Category.BUILD),
        Manifest.Dependency(name="setuptools", version="69.0.3", type=Manifest.Dependency.Type.PIP,
                          category=Manifest.Dependency.Category.BUILD),
        Manifest.Dependency(name="wheel", version="0.42.0", type=Manifest.Dependency.Type.PIP,
                          category=Manifest.Dependency.Category.BUILD),
        Manifest.Dependency(name="packaging", version="25.0.0", type=Manifest.Dependency.Type.PIP,
                          category=Manifest.Dependency.Category.BUILD),
        Manifest.Dependency(name="tomli-w", version="1.0.0", type=Manifest.Dependency.Type.PIP,
                          category=Manifest.Dependency.Category.BUILD)
    ],
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 16), 
                         author=__parent__.authors.rraudzus,
                         notes=["Initial definition of pylium.crowbar package manifest."])
    ]
)


class Crowbar(Header):
    """
    Installer and package management system for Pylium

    This class provides functionality to:
    - Install and setup the Pylium system
    - Manage packages and dependencies
    - Perform runtime installations
    - Repair and update the system
    """

    __manifest__ : Manifest = __manifest__.createChild(
        location=Manifest.Location(module=__name__, classname=__qualname__),
        description="The Crowbar installer and package management system.",
        status=Manifest.Status.Development,
        frontend=Manifest.Frontend.CLI,
        dependencies=[],
        changelog=[
            Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,6,16), author=__parent__.authors.rraudzus,
                               notes=["Initial implementation of the Crowbar installer",
                                      "Added basic dependency management",
                                      "Support for pip and system dependencies"]),
            Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025,6,20), author=__parent__.authors.rraudzus,
                               notes=["Fixed list_dependencies function routing",
                                      "Improved CLI integration with proper function binding",
                                      "Enhanced stability and reliability of dependency listing"])
        ]
    )

    _default_instance: "Crowbar" = None
    _default_lock = threading.Lock()
 

    @classmethod
    def getDependencies(cls, path: str = "", recursive: bool = True, type_filter: str = None, category_filter: str = None) -> Dict[str, List[Manifest.Dependency]]:
        """
        Get the dependencies of the given object path
        """

        manifest = Manifest.getManifest(path)

        if manifest is None:
            raise ValueError(f"No manifest found for path: {path}")

        dependencies = {}

        if recursive:
            for child in manifest.children:
                dependencies.update(cls.getDependencies(child.location.fqnShort, recursive, type_filter, category_filter))

        # Add self to the dependencies if we have elements
        if len(manifest.dependencies) > 0:
            # Root manifest is purely virtual, so it has no location
            if manifest.isRoot:
                dependencies.update({"/": manifest.dependencies})
            else:
                dependencies.update({manifest.location.fqnShort: manifest.dependencies})

        # Filter dependencies based on type and category
        filtered_dependencies = {}
        for module, deps in dependencies.items():
            filtered_deps = []
            for dep in deps:
                # Case insensitive comparison for both filters
                dep_type = dep.type.name.upper()
                dep_category = getattr(dep, 'category', None) and getattr(dep, 'category').name.upper()
                type_match = type_filter is None or dep_type == type_filter.upper()
                category_match = category_filter is None or (dep_category and dep_category == category_filter.upper())
                
                if type_match and category_match:
                    filtered_deps.append(dep)
            if filtered_deps:
                filtered_dependencies[module] = filtered_deps

        return filtered_dependencies

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 


@Manifest.func(__manifest__.createChild(
    location=None,
    description="List the dependencies of the given object path with beautiful formatting and filtering",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 16),
                           author=__parent__.authors.rraudzus,
                           notes=["Added list_dependencies function to list the dependencies of the current package"]),
        Manifest.Changelog(version="0.1.1", date=Manifest.Date(2025, 6, 20),
                           author=__parent__.authors.rraudzus,
                           notes=["Enhanced dependency listing with beautiful tree output",
                                  "Added type and category filtering",
                                  "Added statistics and summary information",
                                  "Added requirements.txt export format via --simple flag",
                                  "Fixed tree visualization with proper branch lines",
                                  "Made type and category filters case-insensitive"])
    ]
))
def list_dependencies(path: str = "", recursive: bool = True, simple: bool = False,
                     type_filter: str = None, category_filter: str = None):
    """List the dependencies of the given object path with beautiful formatting and filtering.

    Args:
        path: The path to the object to list the dependencies for
        recursive: If True, list the dependencies of the dependencies
        simple: If True, output in requirements.txt format (copy-paste ready)
        type_filter: Filter by dependency type (PIP, PYLIUM)
        category_filter: Filter by category (BUILD, RUNTIME, AUTOMATIC, DEVELOPMENT)
    """

    dependencies = Crowbar.getDependencies(path, recursive, type_filter, category_filter)
    
    if simple:
        # Simple requirements.txt format
        all_deps = {}  # Dict to track highest version of each package
        for module_deps in dependencies.values():
            for dep in module_deps:
                if dep.type.name == "PIP":  # Only PIP dependencies for requirements.txt
                    # For source dependencies, always keep the source version
                    if hasattr(dep, 'source') and dep.source:
                        all_deps[dep.name] = f"{dep.name} @ {dep.source}"
                    else:
                        # For version dependencies, keep highest version
                        current = all_deps.get(dep.name, f"{dep.name}==0.0.0")
                        if "==" in current:  # Only compare version deps
                            current_ver = current.split("==")[1]
                            if packaging.version.parse(dep.version) > packaging.version.parse(current_ver):
                                all_deps[dep.name] = f"{dep.name}=={dep.version}"
                        
        for dep in sorted(all_deps.values()):
            print(dep)
        return
    
    # Beautiful output (default)
    # Header
    target = path if path else "pylium"
    print(f"🔍 DEPENDENCY ANALYSIS")
    print(f"📦 Target: {target}")
    print(f"🔗 Recursive: {'Yes' if recursive else 'No'}")
    
    # Show active filters
    filters = []
    if type_filter:
        filters.append(f"Type: {type_filter.upper()}")
    if category_filter:
        filters.append(f"Category: {category_filter.upper()}")
    
    if filters:
        print(f"🔍 Filters: {', '.join(filters)}")
    
    print()
    
    if not dependencies:
        print("✨ No dependencies found!")
        if type_filter or category_filter:
            print("💡 Try removing filters to see all dependencies.")
        return
    
    # Track version differences
    version_conflicts = {}  # name -> {version -> [modules]}
    for module, deps in dependencies.items():
        for dep in deps:
            if dep.type.name == "PIP" and not (hasattr(dep, 'source') and dep.source):
                version_conflicts.setdefault(dep.name, {}).setdefault(dep.version, []).append(module)
    
    # Find highest version for each package
    highest_versions = {}
    for pkg, versions in version_conflicts.items():
        if len(versions) > 1:  # Only track actual conflicts
            highest_versions[pkg] = max(versions.keys(), key=packaging.version.parse)
    
    # Statistics
    total_deps = sum(len(deps) for deps in dependencies.values())
    total_modules = len(dependencies)
    conflict_count = sum(1 for versions in version_conflicts.values() if len(versions) > 1)
    
    print(f"📊 STATISTICS:")
    print(f"   • Total Dependencies: {total_deps}")
    print(f"   • Modules with Dependencies: {total_modules}")
    if conflict_count > 0:
        print(f"   • Version Conflicts: {conflict_count} 🚨")
    
    # Count by category
    category_counts = {}
    for module_deps in dependencies.values():
        for dep in module_deps:
            category = getattr(dep, 'category', None)
            if category:
                category_name = category.name
                category_counts[category_name] = category_counts.get(category_name, 0) + 1
    
    if category_counts:
        print(f"   • By Category:")
        for category, count in sorted(category_counts.items()):
            emoji = {"BUILD": "🔧", "RUNTIME": "⚡", "AUTOMATIC": "🤖", "DEVELOPMENT": "🛠️"}.get(category, "📦")
            print(f"     {emoji} {category}: {count}")
    
    # Count by type
    type_counts = {}
    for module_deps in dependencies.values():
        for dep in module_deps:
            type_name = dep.type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    if type_counts:
        print(f"   • By Type:")
        for type_name, count in sorted(type_counts.items()):
            emoji = {"PIP": "🐍", "PYLIUM": "⚙️"}.get(type_name, "📦")
            print(f"     {emoji} {type_name}: {count}")
    print()
    
    # Dependency Tree
    print(f"🌳 DEPENDENCY TREE:")
    
    for i, (module, deps) in enumerate(dependencies.items()):
        is_last = i == len(dependencies) - 1
        prefix = "└── " if is_last else "├── "
        
        # Module header
        module_emoji = "📦" if module == "/" else "📄"
        print(f"{prefix}{module_emoji} {module}")
        
        # Dependencies
        for j, dep in enumerate(deps):
            is_last_dep = j == len(deps) - 1
            dep_prefix = ("    " if is_last else "│   ") + ("└── " if is_last_dep else "├── ")
            
            # Category emoji
            category = getattr(dep, 'category', None)
            category_emoji = {
                "BUILD": "🔧",
                "RUNTIME": "⚡",
                "AUTOMATIC": "🤖",
                "DEVELOPMENT": "🛠️"
            }.get(category.name if category else "UNKNOWN", "📦")
            
            # Type emoji
            type_emoji = {
                "PIP": "🐍",
                "PYLIUM": "⚙️"
            }.get(dep.type.name, "📦")
            
            # Format dependency string
            dep_str = f"{dep.name} ({dep.version})"
            if hasattr(dep, 'source') and dep.source:
                dep_str += f" @ {dep.source}"
            
            # Add version conflict indicator
            if dep.type.name == "PIP" and not (hasattr(dep, 'source') and dep.source):
                if dep.name in highest_versions:
                    highest = highest_versions[dep.name]
                    if dep.version == highest:
                        dep_str += " ★"  # Highest version
                    else:
                        # Show how many versions lower this is
                        ver_diff = len(version_conflicts[dep.name])
                        dep_str += f" ⚠️[-{ver_diff-1}]"  # Lower version with difference count
            
            print(f"{dep_prefix}{category_emoji} {type_emoji} {dep_str}")
    
    # Show version conflict details if any exist
    if conflict_count > 0:
        print("\n⚠️ VERSION CONFLICTS:")
        for pkg, versions in sorted(version_conflicts.items()):
            if len(versions) > 1:
                print(f"\n  📦 {pkg}:")
                highest = highest_versions[pkg]
                for version, modules in sorted(versions.items(), key=lambda x: packaging.version.parse(x[0]), reverse=True):
                    indicator = "(highest)" if version == highest else ""
                    print(f"    {version} {'★' if version == highest else '⚠️'} {indicator}")
                    for module in sorted(modules):
                        print(f"      • {module}")

@Manifest.func(__manifest__.createChild(
    location=None,
    description="Update dependencies in pyproject.toml based on manifest dependencies",
    status=Manifest.Status.Development,
    frontend=Manifest.Frontend.CLI,
    changelog=[
        Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025, 6, 20),
                         author=__parent__.authors.rraudzus,
                         notes=["Added pyproject_update function to update dependencies in pyproject.toml",
                               "Automatically uses highest version when conflicts exist"])
    ]
))
def pyproject_update(self, path: str = "pyproject.toml"):
    """Update dependencies in pyproject.toml based on manifest dependencies.
    
    Args:
        path: Path to the pyproject.toml file (default: pyproject.toml in current directory)
    """
    import tomllib
    import tomli_w
    
    # Get all dependencies
    dependencies = self.getDependencies("", recursive=True)
    
    # Track highest version of each package
    pkg_versions = {}  # name -> {version, source}
    for module_deps in dependencies.values():
        for dep in module_deps:
            if dep.type.name == "PIP":
                current = pkg_versions.get(dep.name, {"version": "0.0.0", "source": None})
                if hasattr(dep, 'source') and dep.source:
                    # Always keep source dependencies
                    pkg_versions[dep.name] = {"version": dep.version, "source": dep.source}
                elif not current["source"]:  # Don't override source deps with version deps
                    if packaging.version.parse(dep.version) > packaging.version.parse(current["version"]):
                        pkg_versions[dep.name] = {"version": dep.version, "source": None}
    
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        print(f"❌ {path} not found!")
        return
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        return
    
    # Update dependencies
    project = data.setdefault("project", {})
    deps = project.setdefault("dependencies", [])
    
    # Convert existing deps to dict for easier updating
    existing_deps = {}
    for dep in deps:
        if isinstance(dep, str):
            name = dep.split("==")[0].split(">=")[0].split("<=")[0].strip()
            existing_deps[name] = dep
    
    # Update dependencies
    new_deps = []
    for name, info in sorted(pkg_versions.items()):
        if info["source"]:
            new_deps.append(f"{name} @ {info['source']}")
        else:
            new_deps.append(f"{name}=={info['version']}")
    
    project["dependencies"] = new_deps
    
    try:
        with open(path, "wb") as f:
            tomli_w.dump(data, f)
        print(f"✅ Updated {path} with {len(new_deps)} dependencies")
        
        # Show what changed
        added = set(new_deps) - set(existing_deps.values())
        removed = set(existing_deps.values()) - set(new_deps)
        if added:
            print("\n📦 Added dependencies:")
            for dep in sorted(added):
                print(f"  + {dep}")
        if removed:
            print("\n🗑️ Removed dependencies:")
            for dep in sorted(removed):
                print(f"  - {dep}")
                
    except Exception as e:
        print(f"❌ Error writing {path}: {e}")
        return


