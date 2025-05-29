from ._component import Core

class CoreImpl(Core, Core.ImplMixin):
    """
    This is the implementation for the core component.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Impl init: {self.__module__}|{self.__class__.__name__}")

    def testfunc(self):
        print("testfunc from CoreImpl")
        super().testfunc()
