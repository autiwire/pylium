import pytest
import logging
from pylium.core.component import Component

# Configure logging for tests if needed
# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Define components directly within the test file for clarity
class MyTestComponent(Component):
    def __init__(self, *args, **kwargs):
        logger.debug(f"MyTestComponent __init__: {self.__class__.__name__}")
        # Call super to allow args/kwargs pass through
        super().__init__(*args, **kwargs)

class MyTestComponentImpl(MyTestComponent):
    _is_impl = True

    def __init__(self, *args, **kwargs):
        logger.debug(f"MyTestComponentImpl __init__: {self.__class__.__name__}")
        # Call super to allow args/kwargs pass through
        super().__init__(*args, **kwargs)
        # Store args/kwargs for potential assertions
        self.args = args
        self.kwargs = kwargs

def test_component_instantiation_finds_impl():
    """
    Tests that instantiating a header component correctly finds 
    and creates an instance of its implementation sibling.
    """
    logger.info("Running test_component_instantiation_finds_impl...")
    
    # Arrange: Define args and kwargs
    test_args = (1, 2)
    test_kwargs = {'name': 'Test', 'value': 42}
    
    # Act: Instantiate the header component
    instance = MyTestComponent(*test_args, **test_kwargs)
    
    # Assert: Check that the instance is of the Impl class
    assert isinstance(instance, MyTestComponentImpl), \
        f"Instance should be of type MyTestComponentImpl, but got {type(instance)}"
    
    # Assert: Optionally check if args/kwargs were passed correctly
    assert instance.args == test_args
    assert instance.kwargs == test_kwargs
    
    logger.info("Test test_component_instantiation_finds_impl passed.")

def test_component_module_search():
    """
    Tests that the component module search works correctly.
    """
    logger.info("Running test_component_module_search...")
    component_modules = Component._get_all_component_modules()
    assert len(component_modules) > 0, "Expected at least one component module"
    logger.info(f"Found {len(component_modules)} component modules: ")
    for module in component_modules:
        logger.info(f"  Module: {module}")
        logger.info(f"    Description: {module.description}")
        logger.info(f"    Dependencies: {module.dependencies}")
        logger.info(f"    Authors: {module.authors}")
    logger.info("Test test_component_module_search passed.")
