import http
from abc import ABC, abstractmethod
from time import sleep

import psycopg2
from starlette.exceptions import HTTPException

from core.impl_postgresql.database import SemaphoredThreadedConnectionPool
from core.models.product import Product
from core.models.user import User
from core.service_interfaces.product_service import ProductService


class PostgreSQLProductService(ProductService):
    SQL_CREATE_PRODUCT = "INSERT INTO products (name, description, price) VALUES (%(name)s, %(description)s, %(price)s) RETURNING id, name, description, price"

    SQL_LOCK_USER = "SELECT id, balance FROM users WHERE id = %(user_id)s FOR UPDATE;"
    SQL_GET_PRODUCT = "SELECT id, name, price FROM products WHERE id = %(product_id)s"
    SQL_WITHDRAW = f"UPDATE users SET balance = %(balance)s WHERE id = %(user_id)s"
    # SQL_INSERT_ACTIVE_PRODUCT = f"INSERT INTO active_products (user_id, product_id) VALUES (%(user_id)s, %(product_id)s) "

    def get_by_name(self, name: str) -> Product:
        ...

    def create(self, name: str, price: int, description: str) -> Product:
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()
        connection = None

        try:
            connection = pool.getconn()
            with connection.cursor() as cursor:
                params = {
                    "name": name,
                    "description": description,
                    "price": price
                }
                try:
                    cursor.execute(self.SQL_CREATE_PRODUCT, params)
                except psycopg2.errors.UniqueViolation:
                    raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail="Product with this name already exists")
                r = cursor.fetchone()
                connection.commit()
                return Product(id=r[0], name=r[1], description=r[2], price=r[3])
        finally:
            if connection:
                pool.putconn(connection)

    def create_if_not_exist(self, name: str, price: int, description: str) -> Product:
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()
        connection = None

        try:
            connection = pool.getconn()
            with connection.cursor() as cursor:
                params = {
                    "name": name,
                    "price": price,
                    "description": description,
                }
                cursor.execute("INSERT INTO products (name, price, description) "
                               "VALUES (%(name)s, %(price)s, %(description)s) "
                               "ON CONFLICT ON CONSTRAINT products_name_key DO UPDATE SET name = excluded.name "
                               "RETURNING *;", params)
                row = cursor.fetchone()
                connection.commit()

                return self._parse_from_row(row)
        finally:
            if connection:
                pool.putconn(connection)

    @staticmethod
    def _parse_from_row(row: tuple) -> Product:
        return Product(id=row[0], name=row[1], description=row[2], price=row[3])

    def purchase(self, user_id: int, product_id: int):
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()
        connection = None
        try:
            connection = pool.getconn()
            with connection.cursor() as cursor:

                params = {'user_id': user_id}
                cursor.execute(self.SQL_LOCK_USER, params)
                if cursor.rowcount != 1:
                    raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
                user = cursor.fetchone()

                sleep(2)  # for race condition simulation

                params = {'product_id': product_id}
                cursor.execute(self.SQL_GET_PRODUCT, params)
                if cursor.rowcount != 1:
                    raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
                product = cursor.fetchone()

                params = {'balance': user[1] - product[2], 'user_id': user[0]}
                cursor.execute(self.SQL_WITHDRAW, params)

                # params = {'price': product[2], 'user_id': user_id, "product_id": product_id}
                # cursor.execute(self.SQL_INSERT_ACTIVE_PRODUCT, params)

                connection.commit()
        finally:
            if connection:
                pool.putconn(connection)

    def fetch_active(self, user: User):
        raise NotImplementedError()
