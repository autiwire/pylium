from .component import Component

class Core(Component):
    """
    This is the core component of Pylium.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Core init: {self.__module__}|{self.__class__.__name__}")


    def __new__(cls, *args, **kwargs):
        print(f"Core new: {cls.__module__}|{cls.__class__.__name__}")
        return super().__new__(cls, *args, **kwargs)

    def testfunc(self):
        print("testfunc from Core")
