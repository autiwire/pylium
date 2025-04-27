from . import Component

from typing import Optional

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# TEST
from sqlmodel import SQLModel, Field
from sqlalchemy.schema import MetaData

x = MetaData()
y = MetaData()

#class MySQLModel(SQLModel, metadata=x):
#    def __init__(self, *args, **kwargs):
#        logger.debug(f"MySQLModel __init__: {self.__class__.__name__}")
#        super().__init__(*args, **kwargs)

#class MySQLModel2(SQLModel, metadata=x):
#    def __init__(self, *args, **kwargs):
#        logger.debug(f"MySQLModel2 __init__: {self.__class__.__name__}")
#        super().__init__(*args, **kwargs)

class SQLData():
    def __init__(self, metadata: Optional[MetaData] = None, *args, **kwargs):    
        logger.debug(f"SQLData __init__: {self.__class__.__name__}")
        self.metadata = metadata if metadata is not None else MetaData()
        self.model = type("_BaseModel", (SQLModel,), {"metadata": self.metadata}, table=False)

z = MetaData()

x = SQLData(metadata=z)
y = SQLData(metadata=z)

class MyComponent(Component, sqlmodel=x.model, table=True):
    
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


class MyComponent2(Component, sqlmodel=y.model, table=True):
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
engine2 = create_engine("sqlite:///test2.db")

# create tables
from sqlmodel import Field, SQLModel, create_engine, select

# Create the tables in the database
# Uses the metadata associated with MySQLModel
logger.info("Creating database tables...")
x.metadata.create_all(engine)
logger.info("Database tables created (if they didn't exist).")

logger.info("Creating database tables...")
y.metadata.create_all(engine2)
logger.info("Database tables created (if they didn't exist).")
