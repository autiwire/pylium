# The Header Component is the base class for Package which is the base class for all Pylium components
# It is like any other compontent but is able to load other components, especially Impls

from ._component import Component

class Header(Component):
    
    def __init__(self, *args, **kwargs):
        print("Header __init__")
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        print("Header __new__")

        
        

        return super().__new__(cls, *args, **kwargs)

