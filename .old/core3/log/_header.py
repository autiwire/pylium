from pylium.core3.package import Package

import logging
logger = logging.getLogger(__name__)

class Log(Package):
    
    def __init__(self, *args, **kwargs):
        print("Log __init__")
        super().__init__(*args, **kwargs)

    def testfunc(self):
        print("Log testfunc")
        self._log.info("testfunc @ Log")
        
        super().testfunc()

