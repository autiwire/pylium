from ._header import Config

class ConfigImpl(Config, Config.Impl):
    
    def __init__(self, *args, **kwargs):
        print("ConfigImpl __init__")
        super().__init__(*args, **kwargs)

