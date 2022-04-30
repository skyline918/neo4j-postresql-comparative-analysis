from abc import ABC
from typing import Iterable

from core.models.user import User


class UserService(ABC):

    @staticmethod
    def get_users(cursor: int, limit: 50) -> Iterable[User]:
        raise NotImplementedError()
