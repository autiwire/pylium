from pylium.core.module import Module
from pylium.core.package import Package
from pylium.core.project import Project

from typing import ClassVar, List
import datetime
import os # Added for path manipulation

from logging import getLogger

logger = getLogger(__name__)

def _log_class(cls):
    logger.info( f" * {cls.name}")
    logger.debug(f"   - {cls}")

    attr_list = dir(cls)
    for attr in attr_list:
        if not attr.startswith('_'):
            value = getattr(cls, attr)
            # if last in list, add \n\n
            if attr_list.index(attr) == len(attr_list) - 1:
                logger.debug(f"{attr}: {value}\n\n")
            else:
                logger.debug(f"{attr}: {value}")

#    logger.info("--------------------------------")
#    logger.info(f"Object: {cls()}")
#    logger.info("--------------------------------")

class CustomModule(Module):
    """
    A custom module for testing.
    """
#    name: ClassVar[str] = "CUSTOM_A"
    authors: ClassVar[List[Module.AuthorInfo]] = [
        Module.AuthorInfo(name="John Doe", email="john.doe@example.com", since_version="0.0.1", since_date=datetime.date(2025, 5, 10))
    ]
    changelog: ClassVar[List[Module.ChangelogEntry]] = [
        Module.ChangelogEntry(version="0.0.1", notes=["Initial release"], date=datetime.date(2025, 5, 10)),
        Module.ChangelogEntry(version="0.0.2", notes=["Added dependency"], date=datetime.date(2025, 5, 10)),
        Module.ChangelogEntry(version="0.0.3", notes=["Added CustomModule test"], date=datetime.date(2025, 5, 10)),
    ]
    # Add parents dependencies
    dependencies: ClassVar[List[Module.Dependency]] =  [
        Module.Dependency(name="test-custom-dep", type=Module.Dependency.Type.PIP, version="1.33.7"),
    ]
    
logger.info("Listing all modules:")

module_list = Module.list()
module_list.append(CustomModule)

for cls in module_list:
    #logger.info(f"Module: {cls}")
    _log_class(cls)

def test_custom_module_exists():
    """A simple test to check if CustomModule can be referenced."""
    assert CustomModule is not None

def test_custom_module_name():
    """Test the auto-generated name of CustomModule."""
    assert CustomModule.name == "test_module"

def test_custom_module_version():
    """Test the version derived from CustomModule's changelog."""
    assert CustomModule.version == "0.0.3"

def test_custom_module_description():
    """Test the description derived from CustomModule's docstring."""
    assert CustomModule.description == "A custom module for testing."

def test_custom_module_authors():
    """Test the authors list of CustomModule."""
    assert len(CustomModule.authors) == 1
    assert CustomModule.authors[0].name == "John Doe"
    assert CustomModule.authors[0].email == "john.doe@example.com"

def test_custom_module_dependencies():
    """Test the dependencies list of CustomModule."""
    assert len(CustomModule.dependencies) == 3
    dep_names = {dep.name for dep in CustomModule.dependencies}
    assert "pydantic" in dep_names
    assert "fire" in dep_names
    assert "test-custom-dep" in dep_names

    # Check details for the custom one
    custom_dep = next((dep for dep in CustomModule.dependencies if dep.name == "test-custom-dep"), None)
    assert custom_dep is not None
    assert custom_dep.type == Module.Dependency.Type.PIP
    assert custom_dep.version == "1.33.7"

def test_custom_module_file():
    """Test the file attribute of CustomModule."""
    assert CustomModule.file is not None
    assert CustomModule.file.endswith(os.path.join("tests", "test_module.py"))

def test_custom_module_fqn():
    """Test the fully qualified name (fqn) of CustomModule."""
    assert CustomModule.fqn == "test_module"

def test_custom_module_role():
    """Test the role of CustomModule."""
    assert CustomModule.role == Module.Role.BUNDLE

# Note: Testing CustomModule.type would require knowing how pylium.core.module.Module defines its own type,
# as CustomModule inherits it and concrete modules are expected to have a type other than NONE.
# If Module sets a default type (e.g., Module.Type.MODULE), that could be asserted here.

def test_module_list_default_scan():
    """Test Module.list() for default module discovery from src/."""
    # These modules are already imported at the top of this test file,
    # but Module.list() will re-retrieve them from sys.modules after its own import logic.
    found_modules = Module.list()

    assert Module in found_modules, "Module class itself should be found by Module.list()"
    assert Package in found_modules, "Package class should be found by Module.list()"
    assert Project in found_modules, "Project class should be found by Module.list()"

    # CustomModule is defined in this test file ('test_module').
    # Module.list() scans source roots (e.g., 'src/') and imports modules from there.
    # It won't find CustomModule unless 'tests/' is a configured scan path.
    assert CustomModule not in found_modules, "CustomModule should not be found by default scan"

    # Expected count based on known core modules inheriting from Module
    # (Module, Package, Project, InstallerPackage)
    assert len(found_modules) > 3, f"Expected >3 core modules, found {len(found_modules)}"


def test_package_list_filters_by_subclass():
    """Test Package.list() to ensure it only finds subclasses of Package."""
    found_packages = Package.list()

    assert Package in found_packages, "Package class itself should be found by Package.list()"
    assert Project in found_packages, "Project class (subclass of Package) should be found"

    assert Module not in found_packages, "Module class (not a subclass of Package) should NOT be found"

    # Expected count: Package, Project, InstallerPackage
    assert len(found_packages) > 3, f"Expected >3 core packages, found {len(found_packages)}"


def test_custom_module_get_system_dependencies():
    """Test the get_system_dependencies method of CustomModule, building expected dependencies dynamically."""
    
    # Get system dependencies using the method under test (assuming current OS is auto-detected as ubuntu/24.04 or similar)
    system_deps_from_method = CustomModule.get_system_dependencies()

    # Dynamically build the expected list based on CustomModule's dependencies and mapping files
    dynamically_expected_deps_set = set()
    # Module is pylium.core.module.Module, which inherits from _ModuleBase where _pip2sysdep_data_path is defined
    base_data_path = Module._pip2sysdep_data_path 
    test_distro = "ubuntu"  # Consistent with current mapping files for primary test case
    test_version = "24.04"

    for pip_dep in CustomModule.dependencies: # This includes inherited dependencies
        if not hasattr(pip_dep, 'name') or not isinstance(pip_dep.name, str):
            continue # Skip malformed dependency objects
        
        pip_pkg_name = pip_dep.name.lower()
        
        # Paths to check for mapping files
        path_version_specific = os.path.join(base_data_path, test_distro, test_version, f"{pip_pkg_name}.txt")
        path_common = os.path.join(base_data_path, test_distro, "_common_", f"{pip_pkg_name}.txt")

        for dep_file_path in [path_version_specific, path_common]:
            if os.path.exists(dep_file_path) and os.path.isfile(dep_file_path):
                try:
                    with open(dep_file_path, 'r') as f:
                        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        if lines:
                            dynamically_expected_deps_set.update(lines)
                            break # Found and processed for this pip_pkg_name, move to next pip_dep
                except IOError as e:
                    # This could be a pytest.fail() if file readability is critical for the test's premise
                    logger.error(f"Test error reading mapping file {dep_file_path}: {e}")
                    pass 
    
    assert sorted(list(system_deps_from_method)) == sorted(list(dynamically_expected_deps_set)), \
        f"Expected dynamically built system dependencies {sorted(list(dynamically_expected_deps_set))}, but got {sorted(list(system_deps_from_method))}"

    # Test with a non-existent OS to ensure it returns empty and logs appropriately
    non_existent_os_deps = CustomModule.get_system_dependencies(
        distribution_name="nosuchos", 
        distribution_version="1.0"
    )
    assert non_existent_os_deps == [], \
        f"Expected empty list for non-existent OS, got {non_existent_os_deps}"

    # Test with an existing OS but non-existent version (where no specific or common files would match)
    non_existent_version_deps = CustomModule.get_system_dependencies(
        distribution_name="ubuntu",
        distribution_version="0.0.nonexistent"
    )
    assert non_existent_version_deps == [], \
        f"Expected empty list for non-existent OS version, got {non_existent_version_deps}"

