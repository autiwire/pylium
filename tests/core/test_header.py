import unittest
import logging
import sys
from pathlib import Path

# Get the absolute path to the project root (assuming this test file is in tests/core/test_header.py)
project_root = Path(__file__).resolve().parent.parent.parent 

# Add project root to sys.path. This allows importing 'tests.core.demo_h' etc.
# and also helps importlib inside the src code find 'tests.core.demo_impl' via FQN.
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now that project_root is on sys.path, we can use fully qualified paths from the project root.
from tests.core.demo_h import DemoH # Adjusted import
from tests.core.missing_impl_h import MissingImplH # Import the new test class
from tests.core.demo_bundle import DemoBundle # Import the new bundle test class
from pylium.core.header.__header__ import Header, HeaderClassType # For potential future tests

# Configure logging for tests (similar to __main__)
# Test runners might capture this differently, but useful for direct script execution
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestHeaderImplementation(unittest.TestCase):

    def test_convention_instantiation_and_methods(self):
        logger.info("\n--- Test: Instantiation by Convention & Method Calls ---")
        # In DemoH, __implementation__ is set to "tests.core.demo_impl.DemoI"
        # This test will now use that explicit FQN due to the HeaderImpl._find_impl logic.
        try:
            demo_instance = DemoH(name="TestByFQN", value=1, extra_impl_param="PassedToImplViaFQN")
            
            logger.info(f"Successfully instantiated: {type(demo_instance).__name__} (Module: {type(demo_instance).__module__})")
            self.assertEqual(type(demo_instance).__name__, "DemoI", 
                             f"Instance should be DemoI, but got {type(demo_instance).__name__}")
            
            self.assertEqual(demo_instance.name_h, "TestByFQN")
            self.assertEqual(demo_instance.value_h, 1)
            
            self.assertTrue(hasattr(demo_instance, 'extra_impl_param'), "extra_impl_param not found on instance!")
            self.assertEqual(demo_instance.extra_impl_param, "PassedToImplViaFQN")

            # Test instance methods
            header_method_result = demo_instance.header_method()
            logger.info(f"Calling header_method: {header_method_result}")
            self.assertEqual(header_method_result, "Header method from DemoH: TestByFQN")

            impl_method_result = demo_instance.impl_method()
            logger.info(f"Calling impl_method: {impl_method_result}")
            self.assertEqual(impl_method_result, "Impl method from DemoI: TestByFQN, extra: PassedToImplViaFQN")

            # Test class methods
            impl_cm_result = demo_instance.__class__.impl_class_method()
            logger.info(f"Calling impl_class_method via instance.__class__: {impl_cm_result}")
            self.assertEqual(impl_cm_result, "Class method from DemoI (called on DemoI), header_static: Defined in DemoH, impl_static: Defined in DemoI")

            header_cm_override_result = demo_instance.__class__.header_class_method()
            logger.info(f"Calling header_class_method (overridden) via instance.__class__: {header_cm_override_result}")
            self.assertEqual(header_cm_override_result, "OVERRIDDEN Class method from DemoH, now in DemoI (called on DemoI)")
            
            header_cm_original_result = DemoH.header_class_method()
            logger.info(f"Calling header_class_method directly on DemoH: {header_cm_original_result}")
            self.assertEqual(header_cm_original_result, "Class method from DemoH (called on DemoH), static var: Defined in DemoH")

        except Exception as e:
            logger.error(f"Error during test_convention_instantiation_and_methods: {e}", exc_info=True)
            self.fail(f"Test failed with exception: {e}")

    def test_missing_implementation(self):
        logger.info("\n--- Test: Missing Implementation ---")
        with self.assertRaisesRegex(RuntimeError, 
                                   r"Component '.*MissingImplH' \(a Header\) requires an Implementation, but none was found"):
            logger.debug("Attempting to instantiate MissingImplH, expecting RuntimeError...")
            _ = MissingImplH(val=123)
        logger.info("Successfully caught expected RuntimeError for missing implementation.")

    def test_bundle_instantiation(self):
        logger.info("\n--- Test: Bundle Class Instantiation ---")
        try:
            bundle_instance = DemoBundle(name="TestBundle", bundle_val=42)
            logger.info(f"Successfully instantiated: {type(bundle_instance).__name__} (Module: {type(bundle_instance).__module__})")

            self.assertIsInstance(bundle_instance, DemoBundle, "Instance should be DemoBundle")
            self.assertEqual(type(bundle_instance).__name__, "DemoBundle",
                             f"Instance type name should be DemoBundle, but got {type(bundle_instance).__name__}")
            
            # Test __class_type__
            self.assertEqual(bundle_instance.__class_type__, Header.ClassType.Bundle, 
                             "Bundle instance __class_type__ should be Bundle")

            # Test attributes
            self.assertEqual(bundle_instance.name, "TestBundle")
            self.assertEqual(bundle_instance.bundle_val, 42)
            self.assertEqual(bundle_instance.get_name(), "TestBundle")
            self.assertEqual(bundle_instance.get_bundle_val(), 42)

            # Test instance method
            method_result = bundle_instance.bundle_method()
            logger.info(f"Calling bundle_method: {method_result}")
            self.assertEqual(method_result, "Method from DemoBundle 'TestBundle', value=42")

            # Test class method (via instance and directly on class)
            cm_via_instance_result = bundle_instance.__class__.bundle_class_method()
            logger.info(f"Calling bundle_class_method via instance: {cm_via_instance_result}")
            self.assertEqual(cm_via_instance_result, "Class method from DemoBundle, static: In Bundle Static")
            
            cm_via_class_result = DemoBundle.bundle_class_method()
            logger.info(f"Calling bundle_class_method via class: {cm_via_class_result}")
            self.assertEqual(cm_via_class_result, "Class method from DemoBundle, static: In Bundle Static")

            # Test static method
            sm_result = DemoBundle.bundle_static_method()
            logger.info(f"Calling bundle_static_method: {sm_result}")
            self.assertEqual(sm_result, "Static method from DemoBundle")
            
            sm_via_instance_result = bundle_instance.bundle_static_method()
            logger.info(f"Calling bundle_static_method via instance: {sm_via_instance_result}")
            self.assertEqual(sm_via_instance_result, "Static method from DemoBundle")

        except Exception as e:
            logger.error(f"Error during test_bundle_instantiation: {e}", exc_info=True)
            self.fail(f"Test failed with exception: {e}")

    # Placeholder for Test 2: Using __implementation__ FQN string
    # def test_explicit_implementation_fqn(self):
    #     logger.info("\n--- Test: Explicit __implementation__ FQN ---")
    #     # Setup: Modify DemoH or create a new Header class with __implementation__ set
    #     # For example, create TempDemoH in this test file:
    #     # class TempDemoH(Header):
    #     #     __class_type__ = HeaderClassType.Header
    #     #     __implementation__ = "pylium.core.header.demo_impl.DemoI" # Assuming DemoI can serve it
    #     #     def __init__(self, name, value, **kwargs): # Ensure kwargs for extra params
    #     #         super().__init__(name=name, value=value, **kwargs)
    #     #         self.name_h = name
    #     # instance = TempDemoH(name="TestExplicitFQN", value=2, extra_impl_param="ForExplicit")
    #     # self.assertEqual(type(instance).__name__, "DemoI")
    #     # ... more assertions ...
    #     pass # Remember to implement

    # Placeholder for Test 3: Bundle class
    # def test_bundle_instantiation(self):
    #     logger.info("\n--- Test: Bundle Class Instantiation ---")
    #     # Setup: Define a Bundle class
    #     # class DemoBundle(Header):
    #     #     __class_type__ = HeaderClassType.Bundle
    #     #     STATIC_VAR_BUNDLE = "In Bundle"
    #     #     def __init__(self, name):
    #     #         super().__init__(name=name) # if Header.__init__ takes name
    #     #         self.name = name
    #     #         logger.info(f"DemoBundle __init__ for {self.name}")
    #     #     def bundle_method(self): return f"Method from {self.name}"
    #     #     @classmethod
    #     #     def bundle_class_method(cls): return f"Class method from {cls.__name__}"

    #     # instance = DemoBundle(name="TestBundleInstance")
    #     # self.assertEqual(type(instance).__name__, "DemoBundle")
    #     # self.assertEqual(instance.name, "TestBundleInstance")
    #     # self.assertEqual(instance.bundle_method(), "Method from TestBundleInstance")
    #     # self.assertEqual(instance.__class__.bundle_class_method(), "Class method from DemoBundle")
    #     pass # Remember to implement

if __name__ == '__main__':
    unittest.main() 