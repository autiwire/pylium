from sqlmodel import SQLModel
from ._model_meta import ModelMetaclass

from typing import Optional, ClassVar

import logging
logger = logging.getLogger(__name__)

class Model(SQLModel, metaclass=ModelMetaclass, table=False):
    
    def __init__(self, *args, **kwargs):
        logger.debug(f"Model __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        logger.debug(f"Model __new__: {cls.__name__}")
        return super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        logger.debug(f"Model __init_subclass__: {cls.__name__}")
        super().__init_subclass__(**kwargs)
