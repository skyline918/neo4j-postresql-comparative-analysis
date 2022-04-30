from abc import ABC
from typing import Iterable

from core.models.user import User
from core.service_interfaces.user_service import UserService


class Neo4jUserService(UserService):

    @staticmethod
    def get_users(cursor: int, limit: 50) -> Iterable[User]:
        raise NotImplementedError()
