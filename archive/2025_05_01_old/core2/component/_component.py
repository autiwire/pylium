from ._impl import ImplMixin
from typing import ClassVar, Type
from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass

import sys
import importlib
import pathlib
import inspect
import logging

log = logging.getLogger(__name__)

# Custom Metaclass
class ComponentMetaclass(SQLModelMetaclass):
    def __new__(mcls, name, bases, namespace, sqlmodel: Type[SQLModel] = None, **kwargs):
        log.debug(f"ComponentMetaclass: Creating class '{name}'")
        log.debug(f"  Original bases: {bases}")
        log.debug(f"  Received sqlmodel kwarg: {sqlmodel}")
        log.debug(f"  Other kwargs: {kwargs}")

        sqlmodel_base_arg = sqlmodel

        sqlmodel_base_to_use = SQLModel
        if sqlmodel_base_arg is not None:
            if not isinstance(sqlmodel_base_arg, type) or not issubclass(sqlmodel_base_arg, SQLModel):
                 raise TypeError(f"Parameter 'sqlmodel=' for class '{name}' must be a subclass of SQLModel, got {sqlmodel_base_arg}")
            sqlmodel_base_to_use = sqlmodel_base_arg
            log.debug(f"  Using specified sqlmodel base: {sqlmodel_base_to_use.__name__}")
        else:
             log.debug(f"  Using default sqlmodel base: {sqlmodel_base_to_use.__name__}")

        # --- Corrected Base Construction Logic --- 
        final_bases_list = list(bases) # Start with original bases
        sqlmodel_found = False
        # Check if any SQLModel base is already present in the original definition
        for base in bases:
            if isinstance(base, type) and issubclass(base, SQLModel):
                sqlmodel_found = True
                log.debug(f"  Found existing SQLModel base in definition: {base.__name__}")
                # We could optionally check if base is compatible with sqlmodel_base_to_use here
                break 

        # If no SQLModel base was explicitly provided in the class definition bases,
        # ensure the determined one (default or from sqlmodel= kwarg) is added.
        if not sqlmodel_found:
             # Insert the required SQLModel base, typically early in the MRO
             final_bases_list.insert(0, sqlmodel_base_to_use)
             log.debug(f"  Added {sqlmodel_base_to_use.__name__} to bases as none was found in definition.")
        # --- End Corrected Logic --- 

        final_bases = tuple(final_bases_list)
        log.debug(f"  Final bases tuple: {final_bases}")

        # Handle 'table' default: Add table=False ONLY if not explicitly provided
        # AND if we are using the default SQLModel base.
        if 'table' not in kwargs and sqlmodel_base_to_use is SQLModel and not sqlmodel_found:
             kwargs['table'] = False
             log.debug(f"  Added default table=False kwarg")
        elif 'table' in kwargs:
             log.debug(f"  User specified table={kwargs['table']}")

        # Call the SQLModelMetaclass's __new__ with the potentially modified bases
        # and kwargs. It handles 'table' and other SQLModel class setup.
        new_cls = super().__new__(mcls, name, final_bases, namespace, **kwargs)
        log.debug(f"  ComponentMetaclass finished creating: {new_cls.__name__}")
        return new_cls

# Main Component class using the custom metaclass
# No need to inherit SQLModel here; the metaclass adds it.
class Component(metaclass=ComponentMetaclass):
    """
    Base class for Pylium components. Dynamically inherits from SQLModel.

    Define components like:
      `class MyComp(Component): ...` (uses default SQLModel, table=False)
      `class MyTableComp(Component, table=True): ...` (uses default SQLModel, table=True)
      `class MyCustomComp(Component, sqlmodel=MyBase): ...` (uses MyBase, table=False assumed by MyBase)
      `class MyCustomTableComp(Component, sqlmodel=MyBase, table=True): ...` (uses MyBase, table=True)
    """

    ImplMixin: ClassVar = ImplMixin

    # Define if this component is a base component
    # When inherited, childs can iterate back to this component and get the
    # file name of the base component (e.g. for impl discovery)
    # base compontents should always be packages, not modules (_component.py, not <basename>_component.py)
    # This is required for automatic component discovery (especially other than impl)
    # This way custom files can be automatically loaded by the component baseclass
    is_base_component: ClassVar = True

    @staticmethod
    def has_direct_base_subclass(A: type, B: type) -> bool:
        """
        Returns True if A has B (or a subclass of B) as a direct base class.
        Handles potential TypeErrors if A.__bases__ is not available.
        """
        try:
             # Check direct bases only
             return any(base is B or (isinstance(base, type) and issubclass(base, B)) for base in A.__bases__)
        except AttributeError:
             log.warning(f"Could not access __bases__ for type {A} during check.")
             return False

    @classmethod
    def is_impl_class(cls) -> bool:
        """
        Returns True if cls is an Impl class (directly inheriting ImplMixin).
        """
        return cls.has_direct_base_subclass(cls, cls.ImplMixin)

    @classmethod
    def is_package(cls) -> bool:
        """
        Returns True if cls is a package. A package should have a _component.py file and an _impl.py file.
        It can have other files, but the two are required.
        A component can have additional parts, which can be loaded by their baseclass.        

        Structure:
        - package        
          - _component.py
          - _impl.py
          - _<other_component_part>.py

        First the module of our own baseclass must be determined.         
        
          
        """
        
        base_class = cls.__bases__[0]

        
        print(f"Base class: {base_class.__module__}")
        print(f"Base class file: {inspect.getfile(base_class)}")
        print(f"Base class file path: {pathlib.Path(inspect.getfile(base_class))}")
        print(f"Base class file path name: {pathlib.Path(inspect.getfile(base_class)).name}")
        print(f"Base class file path name: {pathlib.Path(inspect.getfile(base_class)).name}")


        # Follow from cls to case and print is_base_component
        current_cls = cls
        while current_cls is not None:
            print(f"Current class: {current_cls.__name__}, is_base_component: {current_cls.is_base_component}")
            current_cls = current_cls.__bases__[0]

        return False
        
    
    @classmethod
    def is_module(cls) -> bool:
        """
        Returns True if cls is a module. A module should at least have a <basename>_component.py file and a <basename>_impl.py file.
        It can have other files, but the two are required.
        Omitting the <basename> will make the component a package instead of a module.

        Structure:
        - module
          - <basename>_component.py
          - <basename>_impl.py
          - <basename>_<other_component_part>.py
        """
        return not cls.__module__.endswith(".__init__")

    # __init__ needs to correctly call the SQLModel init eventually via super()
    def __init__(self, *args, **kwargs):
        log.debug(f"Component __init__: {self.__module__}|{self.__class__.__name__} with bases {self.__class__.__bases__}")
        # super() should chain correctly to SQLModel's init thanks to MRO set by metaclass
        try:
            super().__init__(*args, **kwargs)
        except TypeError as e:
            log.error(f"Potential issue in __init__ call for {self.__class__.__name__}: {e}. Args: {args}, Kwargs: {kwargs}")
            # If SQLModel base __init__ has different signature, this might fail.
            # Consider alternative initialization if needed, but standard super() is preferred.
            pass # Or raise specific error

    # __new__ handles implementation discovery
    def __new__(cls, *args, **kwargs):
        log.debug(f"Component __new__: {cls.__module__}|{cls.__class__.__name__}")

        # If defining an Impl class directly (it should inherit ImplMixin)
        if cls.is_impl_class():
             log.debug(f"  Creating Impl class instance {cls.__name__}")
             # super() will call the next __new__ in the MRO (e.g., SQLModel.__new__)
             instance = super().__new__(cls)
             return instance

        # --- Implementation Discovery Logic --- 
        log.debug(f"  Starting implementation discovery for {cls.__name__}")
        component_module = sys.modules[cls.__module__]
        impl_module_name = None
        impl_module = None

        try:
            component_file_path = pathlib.Path(inspect.getfile(component_module))
            component_dir = component_file_path.parent
            log.debug(f"  Component file path: {component_file_path}")
            log.debug(f"  Component directory: {component_dir}")

            # Case a) Package structure
            if component_file_path.name == "_component.py":
                impl_module_name = f"{component_module.__package__}._impl"
                impl_file_path = component_dir / "_impl.py"
                log.debug(f"  Case a) Expecting impl module: {impl_module_name} at {impl_file_path}")
                if impl_file_path.exists():
                    impl_module = importlib.import_module(impl_module_name)
                else:
                    log.warning(f"  Implementation file not found at {impl_file_path}")

            # Case b) Module structure
            elif component_file_path.name.endswith("_component.py"):
                base_name = component_file_path.stem.replace("_component", "")
                impl_module_simple_name = f"{base_name}_impl"
                impl_module_name = f"{component_module.__package__}.{impl_module_simple_name}" if component_module.__package__ else impl_module_simple_name
                impl_file_path = component_dir / f"{impl_module_simple_name}.py"
                log.debug(f"  Case b) Expecting impl module: {impl_module_name} at {impl_file_path}")
                if impl_file_path.exists():
                     impl_module = importlib.import_module(impl_module_name)
                else:
                    log.warning(f"  Implementation file not found at {impl_file_path}")
            else:
                 log.warning(f"  Component file {component_file_path} does not match expected naming patterns")

        except (ImportError, AttributeError, TypeError, ValueError) as e:
            log.error(f"  Error during implementation discovery setup for {cls.__name__}: {e}", exc_info=True)
            # Fall through to raise error later

        impl_cls = None
        if impl_module:
            log.debug(f"  Searching for Impl class in module: {impl_module_name}")
            for name, obj in inspect.getmembers(impl_module):
                # Check: Is it a class? Does it directly inherit ImplMixin? Does it directly inherit the Component (cls)? Is it not ImplMixin itself?
                if inspect.isclass(obj) and cls.has_direct_base_subclass(obj, cls.ImplMixin) and cls.has_direct_base_subclass(obj, cls) and obj is not cls.ImplMixin:
                    if impl_cls is not None:
                        log.warning(f"  Multiple implementation classes found in {impl_module_name}. Using {impl_cls.__name__}.")
                        break # Use the first one found
                    impl_cls = obj
            
            if impl_cls:
                log.debug(f"  Found implementation class: {impl_cls.__name__}. Instantiating it.")
                instance = impl_cls(*args, **kwargs) # Instantiate the Impl class
                return instance
            else:
                log.warning(f"  No suitable Impl class found in {impl_module_name}")
        
        # If no impl_module found or no suitable class in the module
        raise ValueError(f"Pylium: No suitable implementation class found for {cls.__name__}. Searched module: {impl_module_name or 'Not Found/Import Error'}")

