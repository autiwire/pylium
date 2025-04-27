from ._component import TestCore

from pylium.core.component import Component
from pylium.core._impl import CoreImpl

class TestCoreImpl(TestCore, Component.ImplMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def testfunc(self):
        print(f"testfunc from TestCoreImpl")
        super().testfunc()