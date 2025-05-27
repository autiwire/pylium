# Import the component module instead of the specific class
import pylium.core.component

from ._model import _Model
from ._model_meta import _ModelMetaclass

from typing import ClassVar
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# Remove the lazy import helper
# def _get_component() -> type:
#     from pylium.core.component import _Component
#     return _Component

# Access _Component via the module
class _Database(pylium.core.component._Component, table=False):
    """
    Base class for all databases.
    """

    Model: ClassVar[_Model] = _Model
    ModelMetaclass: ClassVar[_ModelMetaclass] = _ModelMetaclass

    class Settings(BaseSettings):
        url: str

    settings = Settings()

    def __init__(self, url: str):
        self.url = url

