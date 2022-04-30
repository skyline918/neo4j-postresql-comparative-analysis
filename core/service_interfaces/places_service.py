from abc import ABC, abstractmethod
from typing import Iterable, List

from core.models.place import Place
from core.models.user import User


class PlacesService(ABC):

    @abstractmethod
    def get_closest_respect_advertising(self, lat: float, long: float, limit: int) -> Iterable[Place]:
        raise NotImplementedError()

    @abstractmethod
    def batch_upsert(self, places: List[Place]):
        raise NotImplementedError()

    @abstractmethod
    def drop_data(self):
        raise NotImplementedError()
