import http
from time import sleep

import neo4j
from neo4j import Transaction, Result, Record
from neo4j.graph import Node
from starlette.exceptions import HTTPException

from core.models.product import Product
from core.models.user import User
from core.service_interfaces.product_service import ProductService


class Neo4jProductService(ProductService):

    CQL_CREATE_PRODUCT = "CREATE (p:Product {name: $name, price: $price, description: $description}) RETURN p"

    def get_by_name(self, name: str) -> Product:
        from app import Application
        session: neo4j.Session = Application.database.get_session()
        with session:
            result: Result = session.run(query="MATCH (p:Product {name: $name}) RETURN p", name=name)
            data: Node = result.single().value()
            return Product(id=data.id, name=data.get("name"), description=data.get("description"), price=data.get('price'))

    def create(self, name: str, price: int, description: str) -> Product:
        from app import Application
        session: neo4j.Session = Application.database.get_session()
        with session:
            n: Node = session.write_transaction(self._create_product_transaction, name, price, description)
            return Product(id=n.id, name=n.get("name"), price=n.get('price'), description=n.get('description'))

    def create_if_not_exist(self, name: str, price: int, description: str) -> Product:
        try:
            product = self.create(name=name, description="", price=100)
        except HTTPException as ignored:
            product = self.get_by_name(name)

        return product

    def purchase(self, user_id: int, product_id: int):
        from app import Application

        session: neo4j.Session = Application.database.get_session()
        with session:
            session.write_transaction(self._race_condition_solving_purchase_transaction, user_id=user_id, product_id=product_id)

    def fetch_active(self, user: User):
        raise NotImplementedError()

    @staticmethod
    def _race_condition_solving_purchase_transaction(tx: Transaction, user_id, product_id):
        match_user_locking = "MATCH (u:User) WHERE ID(u) = $user_id CALL apoc.lock.nodes([u]) RETURN u"
        match_product = "MATCH (p:Product) WHERE ID(p) = $product_id RETURN p"
        update_balance = "MATCH (u:User) WHERE ID(u) = $user_id SET u.balance = $balance"

        result: Result = tx.run(match_user_locking, user_id=user_id)
        sleep(3)  # race condition 99.9% guarantee
        balance = result.single().value().get("balance")
        result = tx.run(match_product, product_id=product_id)
        price = result.single().value().get("price")

        tx.run(update_balance, user_id=user_id, balance=balance - price)

    @staticmethod
    def _create_product_transaction(tx: Transaction, name: str, price: int, description: str):
        try:
            result = tx.run(Neo4jProductService.CQL_CREATE_PRODUCT, name=name, price=price, description=description)
            return result.values()[0][0]
        except neo4j.exceptions.ConstraintError:
            raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail="Product with this name already exists")

