from pylium.core import Core

class TestCore(Core):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def testfunc(self):
        print(f"testfunc from TestCore")
        super().testfunc()
