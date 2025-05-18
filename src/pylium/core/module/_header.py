from abc import ABC, abstractmethod, ABCMeta

from typing import ClassVar, List, Optional, Type, Any, Generator, Tuple, Callable

from logging import getLogger
logger = getLogger(__name__)

class _HeaderAttribute(ABC):
    def __init__(self, processor: Callable, requires: List[str], always_run_processor: bool = False):
        self.processor = processor
        self.requires = requires
        self.always_run_processor = always_run_processor

class Info(ABC):
    authors: ClassVar[List[_HeaderAttribute]] = _HeaderAttribute(
        processor=lambda cls: cls.authors,
        requires=["authors"],
        always_run_processor=True
    )
    changelog: ClassVar[List[_HeaderAttribute]] = _HeaderAttribute(
        processor=lambda cls: cls.changelog,
        requires=["changelog"],
        always_run_processor=True
    )
    dependencies: ClassVar[List[_HeaderAttribute]] = _HeaderAttribute(
        processor=lambda cls: cls.dependencies,
        requires=["dependencies"],
        always_run_processor=True
    )

class _HeaderMeta(ABCMeta):
    def __str__(cls):
        return f"HeaderMeta {cls.__name__}"

class _Header(ABC, metaclass=_HeaderMeta):
    __info__: ClassVar[Info] = Info()

    def __str__(cls):
        return f"Header {cls.__name__}"


