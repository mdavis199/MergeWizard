from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import List, Union


class Status(IntEnum):
    Info = 0
    Warn = auto()
    Error = auto()
    Success = auto()
    Debug = auto()


class ILogger(ABC):
    @abstractmethod
    def info(self, value: Union[str, List[str]]):
        pass

    @abstractmethod
    def warn(self, value: Union[str, List[str]]):
        pass

    @abstractmethod
    def error(self, value: Union[str, List[str]]):
        pass

    @abstractmethod
    def success(self, value: Union[str, List[str]]):
        pass

    @abstractmethod
    def debug(self, value: Union[str, List[str]]):
        pass

    @abstractmethod
    def log(self, value: Union[str, List[str]], status: Status):
        pass
