from . import Component

from typing import Optional
from sqlalchemy.schema import MetaData
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# TEST
from sqlmodel import SQLModel, Field

# Define separate metadata instances
y = MetaData()
y2 = MetaData()

# Remove BaseModel1, BaseModel2 definitions
# class BaseModel1(Model): ...
# class BaseModel2(Model): ...

# Define components passing metadata as kwarg
class MyComponent(Component, metadata=y, table=True):
    
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


class MyComponent2(Component, metadata=y2, table=True):

    xyz: Optional[int] = Field(default=None, primary_key=True)
    rst: str

    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponent2 __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

class MyComponentImpl2(MyComponent2, MyComponent2.ImplMixin):
    
    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponentImpl2 __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

# MyComponent3 inherits MyComponent, should inherit metadata=y implicitly
class MyComponent3(MyComponent): # No need to repeat metadata=y here
    extra_field: str = Field(default="default_value")
    another_field: Optional[str] = None

    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponent3 __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

class MyComponent3Impl(MyComponent3, MyComponent3.ImplMixin):

        def __init__(self, *args, **kwargs):
            logger.debug(f"MyComponent3Impl __init__: {self.__class__.__name__}")
            super().__init__(*args, **kwargs)

print("Creating MyComponent")
c = MyComponent(name="John", secret_name="Doe", age=30)
print(c)

print("Creating MyComponent3")
c3 = MyComponent3(name="Jane", secret_name="Smith")
print(c3)

# create database
from sqlmodel import create_engine
engine = create_engine("sqlite:///test.db")
engine2 = create_engine("sqlite:///test2.db")

# create tables using the specific metadata instances
logger.info("Creating database tables using metadata y...")
y.create_all(engine)
logger.info("Creating database tables using metadata y2...")
y2.create_all(engine2)
logger.info("Database tables created (if they didn't exist).")
