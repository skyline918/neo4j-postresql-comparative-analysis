import http
from abc import ABC, abstractmethod

from starlette.exceptions import HTTPException

from core.models.product import Product
from core.models.user import User


class ProductService(ABC):

    @abstractmethod
    def create(self, name: str, price: int, description: str) -> Product:
        raise NotImplementedError()

    @abstractmethod
    def purchase(self, user_id: int, product_id: int):
        raise NotImplementedError()

    @abstractmethod
    def fetch_active(self, user: User):
        raise NotImplementedError()
