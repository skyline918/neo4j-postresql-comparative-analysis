import http

import neo4j
from neo4j import Transaction
from neo4j.graph import Node
from starlette.exceptions import HTTPException

from core.models.product import Product
from core.models.user import User
from core.service_interfaces.product_service import ProductService


class Neo4jProductService(ProductService):

    CQL_CREATE_PRODUCT = "CREATE (p:Product {name: $name, price: $price, description: $description}) RETURN p"

    def create(self, name: str, price: int, description: str) -> Product:
        from app import Application
        session: neo4j.Session = Application.database.get_session()
        with session:
            n: Node = session.write_transaction(self._create_product_transaction, name, price, description)
            return Product(id=n.id, name=n.get("name"), price=n.get('price'), description=n.get('description'))

    def purchase(self, user_id: int, product_id: int):
        ...

    def fetch_active(self, user: User):
        raise NotImplementedError()

    @staticmethod
    def _create_product_transaction(tx: Transaction, name: str, price: int, description: str):
        try:
            result = tx.run(Neo4jProductService.CQL_CREATE_PRODUCT, name=name, price=price, description=description)
            return result.values()[0][0]
        except neo4j.exceptions.ConstraintError:
            raise HTTPException(status_code=http.HTTPStatus.CONFLICT, detail="Product with this name already exists")

