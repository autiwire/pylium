import dataclasses
from enum import Enum
from typing import List, Optional, Type # Added Type hint
import datetime
import logging
from pydantic_settings import BaseSettings

@dataclasses.dataclass(frozen=True)
class ComponentModuleDependencyType(Enum):
    PYLIUM = "pylium"
    PIP = "pip"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

@dataclasses.dataclass(frozen=True)
class ComponentModuleDependency:
    """
    A dependency for a component module.
    """

    Type = ComponentModuleDependencyType

    name: str
    type: Type
    version: str

    def __str__(self):
        return f"{self.name} ({self.type}) {self.version}"
    
    def __repr__(self):
        return f"{self.name} ({self.type}) {self.version}"
    
@dataclasses.dataclass(frozen=True)
class ComponentModuleAuthorInfo:
    name: str
    email: Optional[str] = None
    since_version: Optional[str] = None
    since_date: Optional[datetime.date] = None

    def __str__(self):
        return f"{self.name} ({self.email}) {self.since_version} {self.since_date}"
    
    def __repr__(self):
        return f"{self.name} ({self.email}) [since: {self.since_version} @ {self.since_date}]"

class ComponentModuleConfig(BaseSettings):
    """
    Configuration for a component module.

    Inherit this and add an instance to __init__() of the component module.
    """

    enabled: bool = True
    cli: bool = False

class ComponentModule:
    """
    Base class for Pylium core component modules

    This helper class is used to do some setup work for component modules.
    
    """

    Dependency = ComponentModuleDependency    
    PYLIUM = Dependency.Type.PYLIUM
    PIP = Dependency.Type.PIP

    AuthorInfo = ComponentModuleAuthorInfo

    Config = ComponentModuleConfig

    def __init__(self, 
            name: str,
            version: str,
            description: str,
            dependencies: List['Dependency'],
            authors: List['AuthorInfo'],
            settings_class: Optional[Type[BaseSettings]] = None,
            logger: Optional[logging.Logger] = None,
            *args, 
            **kwargs):
        
        super().__init__()

        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies if dependencies else []
        self.authors = authors if authors else []
        self._settings_class = settings_class
        self._settings_instance: Optional[BaseSettings] = None
        self.logger = logger if logger else logging.getLogger(f"{self.name}")        

        self.logger.debug(f"Initializing ComponentModule: {name}")

    def __str__(self):
        return f"{self.name}^{self.version}"
    
    def __repr__(self):
        return f"{self.name}^{self.version}"

    def add_dependency(self, name: str, dependency_type: Dependency.Type, version: str):
        """
        Add a dependency to the component module.
        """
        self.dependencies[dependency_type].append(ComponentModule.Dependency(name, dependency_type, version))

    def get_dependencies(self) -> dict[Dependency.Type, list[Dependency]]:
        """
        Get the dependencies of the component module.
        """
        return self.dependencies