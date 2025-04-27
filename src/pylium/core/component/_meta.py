from typing import Type

from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass 
from sqlalchemy.schema import MetaData

import logging
logger = logging.getLogger(__name__)

class ComponentMetaclass(SQLModelMetaclass): # Inherit from SQLModelMetaclass
    """
    Metaclass that allows specifying an additional base class for a component
    via the 'component_base' keyword argument during class definition.

    Example:
        class MyComponent(Component, sqlmodel=MySpecificBase):
            pass
    """

    # Change 'sqlmodel_base' parameter to 'sqlmodel', defaulting to SQLModel
    def __new__(mcls, name, bases, namespace, sqlmodel: Type[SQLModel] = SQLModel, **kwargs):
        logger.debug(f"ComponentMeta creating class '{name}' with original bases {bases}")

        final_bases = list(bases)

        # --- Add the specified SQLModel base (using 'sqlmodel') --- 
        is_already_sql_base = any(issubclass(base, sqlmodel) for base in final_bases if isinstance(base, type))
        # Check against base SQLModel too, to avoid adding the default if a subclass is already present
        is_already_base_sql_model = any(issubclass(base, SQLModel) for base in final_bases if isinstance(base, type))

        if sqlmodel not in final_bases and not is_already_sql_base:
            # Only add if it's not the default AND no other SQLModel is present,
            # OR if it IS the default and no other SQLModel is present.
            if sqlmodel is not SQLModel or not is_already_base_sql_model:
                logger.debug(f"Adding SQLModel base: {sqlmodel.__name__} to '{name}'")
                # Insert early for MRO benefits?
                final_bases.insert(0, sqlmodel)

        # Finalize bases tuple
        if not final_bases:
            final_bases_tuple = (object,)
        else:
            final_bases_tuple = tuple(final_bases)

        logger.debug(f"Final bases for '{name}': {final_bases_tuple}")

        # Call super().__new__, which calls SQLModelMetaclass.__new__
        new_cls = super().__new__(mcls, name, final_bases_tuple, namespace, **kwargs)
        logger.debug(f"Class '{name}' created by ComponentMeta: {new_cls}")
        return new_cls
    

