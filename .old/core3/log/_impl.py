from ._header import Log

import logging
logger = logging.getLogger(__name__)

class LogImpl(Log, Log.Impl):
    
    def __init__(self, *args, **kwargs):
        print("LogImpl __init__")
        super().__init__(*args, **kwargs)

    def testfunc(self):
        print("LogImpl testfunc")
        print(f"DEBUG: Inside LogImpl.testfunc for {self}, checking _log: {hasattr(self, '_log')}")
        self._log.warning(" x testfunc @ LogImpl")

