from ._impl import ImplMixin
from typing import ClassVar
 
from sqlmodel import SQLModel

import sys
import importlib
import pathlib
import inspect

class Component(SQLModel, table=False):
    """
    This is the base class for all Pylium components.

    Inherit from this class to create a new component. 
    Inherit from this new component and the ImplMixin to create an implementation for the component.
    """
    
    ImplMixin: ClassVar = ImplMixin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Component init: {self.__module__}|{self.__class__.__name__}")

    def __new__(cls, *args, **kwargs):
        print(f"Component new: {cls.__module__}|{cls.__class__.__name__}")

        # check if ImplMixin or a subclass of ImplMixin is a direct parent of cls
        # If we are already an ImplMixin, we don't need to create an implementation
        if issubclass(cls, cls.ImplMixin):
            return super().__new__(cls, *args, **kwargs)

        # Get the module and file path of the component class
        component_module = sys.modules[cls.__module__]
        component_file_path = pathlib.Path(inspect.getfile(component_module))
        component_dir = component_file_path.parent

        print(f"Component file path: {component_file_path}")
        print(f"Component directory: {component_dir}")  
        print(f"Component module: {component_module}")

        impl_module_name = None
        impl_module = None
        
        # Case a) Package structure (e.g., src/pylium/comp1/_component.py)
        if component_file_path.name == "_component.py":
            # Construct impl module name relative to the parent package
            impl_module_name = f"{component_module.__package__}._impl"
            impl_file_path = component_dir / "_impl.py"
            print(f"Case a) Package structure detected. Expecting impl module: {impl_module_name} at {impl_file_path}")
            if impl_file_path.exists():
                try:
                    impl_module = importlib.import_module(impl_module_name)
                except ImportError as e:
                    print(f"Error importing implementation module {impl_module_name}: {e}")
            else:
                 print(f"Implementation file not found at {impl_file_path}")

        # Case b) Module structure (e.g., src/pylium/comp1_component.py)
        elif component_file_path.name.endswith("_component.py"):
            base_name = component_file_path.stem.replace("_component", "")
            impl_module_simple_name = f"{base_name}_impl"
            impl_module_name = f"{component_module.__package__}.{impl_module_simple_name}" if component_module.__package__ else impl_module_simple_name
            impl_file_path = component_dir / f"{impl_module_simple_name}.py"
            print(f"Case b) Module structure detected. Expecting impl module: {impl_module_name} at {impl_file_path}")
            if impl_file_path.exists():
                try:
                    impl_module = importlib.import_module(impl_module_name)
                except ImportError as e:
                    print(f"Error importing implementation module {impl_module_name}: {e}")
            else:
                 print(f"Implementation file not found at {impl_file_path}")
        else:
            print(f"Warning: Component file {component_file_path} does not match expected naming patterns (_component.py or *_component.py)")

        impl_cls = None
        if impl_module:
            # Search for the implementation class within the loaded module
            for name, obj in inspect.getmembers(impl_module):
                if inspect.isclass(obj) and cls.has_direct_base_subclass(obj, cls.ImplMixin) and cls.has_direct_base_subclass(obj, cls) and obj is not cls.ImplMixin:
                    if impl_cls is not None:
                        print(f"Warning: Multiple implementation classes found in {impl_module_name}. Using {impl_cls.__name__}.")
                        break # Use the first one found
                    impl_cls = obj
            
            if impl_cls:
                print(f"Found implementation class: {impl_cls.__name__} in {impl_module_name}")
                # Store the found implementation class maybe? 
                # cls._found_impl_cls = impl_cls # Example, depends on desired usage
                instance = impl_cls(*args, **kwargs)
                return instance
            else:
                raise ValueError(f"No implementation class found for {cls.__name__} in {impl_module_name}")
        
        raise ValueError(f"No implementation class found for {cls.__name__} in {impl_module_name}")
    

    @staticmethod
    def has_direct_base_subclass(A: type, B: type) -> bool:
        """
            Returns True if A has B(or a subclass of B) as a direct base class.
        """
        return any(issubclass(base, B) for base in A.__bases__)