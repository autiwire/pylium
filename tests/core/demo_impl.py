from .demo_h import DemoH
from pylium.core.header.__header__ import HeaderClassType

import logging
logger = logging.getLogger(__name__)

class DemoI(DemoH):
    __class_type__ = HeaderClassType.Impl

    STATIC_VAR_IMPL = "Defined in DemoI"

    def __init__(self, name: str, value: int, extra_impl_param: str = "DefaultImpl", **kwargs):
        super().__init__(name=name, value=value, **kwargs)
        self.extra_impl_param = extra_impl_param
        logger.info(f"DemoI ({self.__class__.__name__}) __init__ called for {self.name_h}, extra: {self.extra_impl_param}")

    def impl_method(self):
        logger.info(f"DemoI ({self.__class__.__name__}) impl_method called for {self.name_h}")
        return f"Impl method from DemoI: {self.name_h}, extra: {self.extra_impl_param}"

    @classmethod
    def impl_class_method(cls):
        logger.info(f"DemoI class_method called on cls: {cls.__name__}")
        header_var = hasattr(cls, 'STATIC_VAR_HEADER') and cls.STATIC_VAR_HEADER
        impl_var = hasattr(cls, 'STATIC_VAR_IMPL') and cls.STATIC_VAR_IMPL
        return f"Class method from DemoI (called on {cls.__name__}), header_static: {header_var}, impl_static: {impl_var}"

    @classmethod
    def header_class_method(cls):
        logger.info(f"DemoI OVERRIDE of header_class_method called on cls: {cls.__name__}")
        return f"OVERRIDDEN Class method from DemoH, now in DemoI (called on {cls.__name__})" 