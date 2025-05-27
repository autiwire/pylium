from pylium.core.header.__header__ import Header
import logging

logger = logging.getLogger(__name__)

class DemoBundle(Header):
    __class_type__ = Header.ClassType.Bundle
    STATIC_VAR_BUNDLE = "In Bundle Static"

    def __init__(self, name, bundle_val=0):
        super().__init__() # Call super().__init__ without args as per Header's design
        self.name = name
        self.bundle_val = bundle_val
        logger.debug(f"DemoBundle '{self.name}' initialized with bundle_val={self.bundle_val}")

    def get_name(self):
        return self.name

    def get_bundle_val(self):
        return self.bundle_val

    def bundle_method(self):
        return f"Method from DemoBundle '{self.name}', value={self.bundle_val}"

    @classmethod
    def bundle_class_method(cls):
        return f"Class method from {cls.__name__}, static: {cls.STATIC_VAR_BUNDLE}"

    @staticmethod
    def bundle_static_method():
        return "Static method from DemoBundle" 