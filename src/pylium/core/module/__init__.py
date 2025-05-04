from typing import List, ClassVar

class Module:
    """
    A module is basically a python file or folder.
    """

    name: str
    version: str
    description: str
    dependencies: List[str]
    authors: List[str]
    #settings_class: Optional[Type[ComponentModuleConfig]] = None
    #logger: Optional[logging.Logger] = None

    def __init__(self, 
            name: str, 
            version: str, 
            description: str, 
            dependencies: List[str], 
            authors: List[str],
            *args, 
            **kwargs):
        
        """
        Initialize the Module.
        """
        
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies
        self.authors = authors

    def __str__(self):
        return f"Module: {self.name}"
    
    def __repr__(self):
        return f"Module: {self.name}"
    
__all__ = ["Module"]




# def __init__(self, 
#            settings_class: Optional[Type[ComponentModuleConfig]] = None,
#            logger: Optional[logging.Logger] = None,
