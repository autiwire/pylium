# The Header Component is the base class for Package which is the base class for all Pylium components
# It is like any other compontent but is able to load other components, especially Impls

from ._component import Component
from ._impl import Impl

class Header(Component):
    
    def __init__(self, *args, **kwargs):
        print("Header __init__")
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        print("Header __new__")
 
        # TODO: Check if cls is already an Impl
        is_impl: bool = cls.has_direct_base_subclass(cls, Impl)

        if is_impl:
            print("Header is already an Impl")
        else:
            print("Header is not an Impl")

        # We have already the implementation, so we can return it
        if is_impl: 
            return super().__new__(cls, *args, **kwargs)
        
        # We don't have the implementation, so we need to create it
        impl_cls = cls.get_sibling_from_basetype(Impl)
        return impl_cls(*args, **kwargs)

