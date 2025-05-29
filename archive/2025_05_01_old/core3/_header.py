from .package import Package

class Core(Package):
    
    def __init__(self, *args, **kwargs):
        print("Core __init__")
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        print("Core __new__")
        return super().__new__(cls, *args, **kwargs)

