#from . import Header 
#from pylium.core.manifest import Manifest # Ensure this path is correct
#from pylium import __project__

#print(__project__.__manifest__)
#print(Manifest.__manifest__)

#h = Header()

#print(h.__manifest__)

#class X(Header):
#    """
#    This is a test class.
#    """
#    __manifest__ = Manifest(
#        location=Manifest.Location(module=__module__, classname=__qualname__),
#        description="Test class",
#        status=Manifest.Status.Development,
#        dependencies=[],
#        authors=__project__.__manifest__.authors,
#        maintainers=__project__.__manifest__.maintainers,
#        copyright=__project__.__manifest__.copyright,
#        license=__project__.__manifest__.license,
#        changelog=[Manifest.Changelog(version="0.1.0", date=Manifest.Date(2025,1,1), author=__project__.__manifest__.authors.rraudzus, notes=["Initial release"])],
#    )

#print(X.__manifest__)

#print(X.__manifest__.doc)

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the Header class we want to test
from .demo_h import DemoH

logger.info("--- Starting Header/Impl Test ---")

# Test 1: Instantiation by convention (_h -> _impl)
logger.info("\n--- Test 1: Instantiation by Convention ---")
try:
    # Note: DemoI has an extra param 'extra_impl_param'. 
    # We pass it here during DemoH instantiation because __new__ will pass *args, **kwargs along.
    demo_instance = DemoH(name="TestByConvention", value=1, extra_impl_param="PassedToImpl")
    logger.info(f"Successfully instantiated: {type(demo_instance).__name__} (Module: {type(demo_instance).__module__})")
    assert type(demo_instance).__name__ == "DemoI", f"Instance should be DemoI, but got {type(demo_instance).__name__}"
    logger.info(f"Instance name_h: {demo_instance.name_h}")
    logger.info(f"Instance value_h: {demo_instance.value_h}")
    # Check if extra_impl_param was set by DemoI's __init__
    if hasattr(demo_instance, 'extra_impl_param'):
        logger.info(f"Instance extra_impl_param: {demo_instance.extra_impl_param}")
        assert demo_instance.extra_impl_param == "PassedToImpl"
    else:
        logger.error("extra_impl_param not found on instance!")
        assert False, "extra_impl_param not found"

    # Test instance methods
    logger.info(f"Calling header_method: {demo_instance.header_method()}")
    logger.info(f"Calling impl_method: {demo_instance.impl_method()}")

    # Test class methods
    # Call via instance.__class__ to ensure 'cls' is the Impl class
    logger.info(f"Calling impl_class_method via instance.__class__: {demo_instance.__class__.impl_class_method()}")
    logger.info(f"Calling header_class_method (potentially overridden) via instance.__class__: {demo_instance.__class__.header_class_method()}")
    
    # For comparison, call header_class_method directly on DemoH (cls will be DemoH)
    logger.info(f"Calling header_class_method directly on DemoH: {DemoH.header_class_method()}")

except Exception as e:
    logger.error(f"Error during Test 1: {e}", exc_info=True)


# Test 2: Using __implementation__ FQN string (Optional - if you want to test this specifically)
# To make this work, you'd temporarily add to DemoH:
# __implementation__ = "pylium.core.header.demo_impl.DemoI"
# For now, this is implicitly tested if the above works, as _find_impl prioritizes it.

# Test 3: Bundle class (Optional - requires creating a Bundle class)
# class DemoBundle(Header):
#     __class_type__ = HeaderClassType.Bundle
#     def __init__(self, name):
#         self.name = name
#         logger.info(f"DemoBundle __init__ for {self.name}")
# demo_bundle_instance = DemoBundle(name="TestBundle")
# logger.info(f"Bundle instance type: {type(demo_bundle_instance)}")

logger.info("\n--- Header/Impl Test Complete ---")