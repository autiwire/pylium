from . import Component

from typing import Optional

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# TEST
from sqlmodel import SQLModel, Field
from sqlalchemy.schema import MetaData

class MySQLModel(SQLModel):
    metadata = MetaData()
    
    def __init__(self, *args, **kwargs):
        logger.debug(f"MySQLModel __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

class MySQLModel2(SQLModel):
    metadata = MetaData()

    def __init__(self, *args, **kwargs):
        logger.debug(f"MySQLModel2 __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

class MyComponent(Component, sqlmodel=MySQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponent __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)
        

class MyComponentImpl(MyComponent, MyComponent.ImplMixin):
    
    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponentImpl __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)


class MyComponent2(Component, sqlmodel=MySQLModel2, table=True):
    xyz: Optional[int] = Field(default=None, primary_key=True)
    rst: str

    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponent2 __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

class MyComponentImpl2(MyComponent2, MyComponent2.ImplMixin):
    
    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponentImpl2 __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

print("Creating MyComponent")
c = MyComponent()
print(c)

print("Creating MyComponentImpl")
c2 = MyComponentImpl()
print(c2)

# create database
from sqlmodel import create_engine
engine = create_engine("sqlite:///test.db")

# create tables
from sqlmodel import Field, SQLModel, create_engine, select

# Create the tables in the database
# Uses the metadata associated with MySQLModel
logger.info("Creating database tables...")
MySQLModel.metadata.create_all(engine)
logger.info("Database tables created (if they didn't exist).")
