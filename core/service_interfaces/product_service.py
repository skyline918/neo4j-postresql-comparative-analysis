from abc import ABC, abstractmethod

from core.models.product import Product
from core.models.user import User


class ProductService(ABC):

    @abstractmethod
    def get_by_name(self, name: str) -> Product:
        raise NotImplementedError()

    @abstractmethod
    def create(self, name: str, price: int, description: str) -> Product:
        raise NotImplementedError()

    @abstractmethod
    def create_if_not_exist(self, name: str, price: int, description: str) -> Product:
        raise NotImplementedError()

    @abstractmethod
    def purchase(self, user_id: int, product_id: int):
        raise NotImplementedError()

    @abstractmethod
    def fetch_active(self, user: User):
        raise NotImplementedError()
