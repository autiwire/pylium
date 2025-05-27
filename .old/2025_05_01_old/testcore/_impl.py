import logging
log = logging.getLogger(__name__)

from ._component import TestCore

from pylium.core2.component import Component
from pylium.core2._impl import CoreImpl # remove this if problems

class TestCoreImpl(TestCore, CoreImpl, Component.ImplMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def testfunc(self):
        log.debug(f"Entering TestCoreImpl.testfunc for {self}")
        print(f"testfunc from TestCoreImpl")
        super().testfunc()