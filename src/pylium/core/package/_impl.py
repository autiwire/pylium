from ._component import Component

class Impl(Component):
    
    def __init__(self, *args, **kwargs):
        print("Impl __init__")
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        print("Impl __new__")
        return super().__new__(cls, *args, **kwargs)

