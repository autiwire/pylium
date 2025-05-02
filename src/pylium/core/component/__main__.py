from . import Component

from typing import Optional

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Define components passing metadata as kwarg
class MyComponent(Component):
    

    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponent __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)
        

class MyComponentImpl(MyComponent):
    _is_impl = True

    def __init__(self, *args, **kwargs):
        logger.debug(f"MyComponentImpl __init__: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    print("Hello, World!")
    my_component = MyComponent(name="John", secret_name="Doe", age=30)
    print(f"--------------------------------")
    print(my_component)
