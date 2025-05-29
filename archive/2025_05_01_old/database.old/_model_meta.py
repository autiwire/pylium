from typing import Type

from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass 
from sqlalchemy.schema import MetaData

import logging
logger = logging.getLogger(__name__)

class _ModelMetaclass(SQLModelMetaclass): 
    """
    Metaclass that allows specifying database model base class for a component

    Example:
        class MyModel(Model, metadata=MetaData(), table=True):
            pass
    """

    def __new__(mcls, name, bases, namespace, *args, **kwargs):
        logger.debug(f"ModelMetaclass creating class '{name}' with original bases {bases}")
        
        # --- Inject metadata into namespace --- 
        # Pop metadata from kwargs so it doesn't cause issues further up
        metadata = kwargs.pop('metadata', None) 
        if metadata is not None:
            if isinstance(metadata, MetaData):
                logger.debug(f"Injecting metadata into namespace for class '{name}'")
                namespace['metadata'] = metadata
            else:
                 raise TypeError(f"'metadata' keyword argument must be a SQLAlchemy MetaData instance, got {type(metadata)}")
        # ------------------------------------ 

        # Call super().__new__, passing original kwargs *minus metadata*
        # SQLModelMetaclass will find 'metadata' in the namespace if we added it.
        # It will handle other kwargs like 'table=True'.
        new_cls = super().__new__(mcls, name, bases, namespace, *args, **kwargs )
        logger.debug(f"Class '{name}' created by ModelMeta: {new_cls}")
        return new_cls
    

