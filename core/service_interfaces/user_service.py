from abc import ABC
from typing import Iterable

from core.models.user import User


class UserService(ABC):

    def update_balance(self, user: User):
        raise NotImplementedError()

    @staticmethod
    def get_users(cursor: int, limit: 50) -> Iterable[User]:
        raise NotImplementedError()

    def get_by_id(self, user_id) -> User:
        raise NotImplementedError()

    def create_if_not_exist(self, username: str, email: str, password: str) -> User:
        raise NotImplementedError()

