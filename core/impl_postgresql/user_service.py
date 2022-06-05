import datetime
import http
from abc import ABC
from typing import Iterable

import psycopg2

from core.impl_postgresql.database import SemaphoredThreadedConnectionPool
from core.models.user import User
from core.service_interfaces.user_service import UserService


class PostgreSQLUserService(UserService):

    def get_by_id(self, user_id) -> User:
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()
        connection = None
        try:
            connection = pool.getconn()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %(user_id)s", {"user_id": user_id})
                row = cursor.fetchone()
        finally:
            if connection:
                pool.putconn(connection)

        return self._parse_from_row(row)

    def update_balance(self, user: User):
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()
        connection = None

        try:
            connection = pool.getconn()
            with connection.cursor() as cursor:
                params = {
                    "balance": user.balance,
                    "user_id": user.id,
                }
                cursor.execute("UPDATE users SET balance = %(balance)s WHERE id = %(user_id)s", params)
                connection.commit()
        finally:
            if connection:
                pool.putconn(connection)

    @staticmethod
    def get_users(cursor: int, limit: 50) -> Iterable[User]:
        raise NotImplementedError()

    def create_if_not_exist(self, username: str, email: str, password: str) -> User:
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()
        connection = None

        try:
            connection = pool.getconn()
            with connection.cursor() as cursor:
                params = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "created_on": datetime.datetime.now().isoformat()
                }
                cursor.execute("INSERT INTO users (username, email, password, balance, created_on) "
                               "VALUES (%(username)s, %(email)s, %(password)s, 0, %(created_on)s) "
                               "ON CONFLICT ON CONSTRAINT users_username_key DO UPDATE SET username = excluded.username "
                               "RETURNING *;", params)
                row = cursor.fetchone()
                connection.commit()

                return self._parse_from_row(row)
        finally:
            if connection:
                pool.putconn(connection)

    @staticmethod
    def _parse_from_row(row: tuple) -> User:
        return User(id=row[0], email=row[1], username=row[2], password=row[3], balance=row[4], created_on=row[5])
