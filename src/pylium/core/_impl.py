from .package import Package

class CoreImpl(Package.Impl):
    
    def __init__(self, *args, **kwargs):
        print("CoreImpl __init__")
        super().__init__(*args, **kwargs)


    def testfunc(self):
        print("testfunc from CoreImpl")
        super().testfunc()


