from pylium.core3.package import Package

from pydantic import BaseSettings, BaseModel, Field

class Config(Package):
    
    class Settings(BaseSettings):
        pass

    class Model(BaseModel):
        pass

    def __init__(self, *args, **kwargs):
        print("Config __init__")
        super().__init__(*args, **kwargs)



