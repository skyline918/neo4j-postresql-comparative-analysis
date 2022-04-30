from abc import ABC, abstractmethod
from typing import Union

import neo4j


class DatabaseBackend(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_session(self) -> Union[neo4j.Session, int]:
        pass

    @abstractmethod
    def create_schema(self):
        pass

    @abstractmethod
    def get_pool(self):
        pass
