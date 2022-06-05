import datetime
from abc import ABC
from typing import Iterable, Union

from neo4j import Transaction, Result, Record
from neo4j.graph import Node

from core.models.user import User
from core.service_interfaces.user_service import UserService


class Neo4jUserService(UserService):

    def get_by_id(self, user_id: int) -> User:
        from app import Application
        session = Application.database.get_session()
        with session:
            result = session.run("MATCH (u:User) WHERE ID(u) = $user_id RETURN u", user_id=user_id)
            node = result.single().value()
            return self._parse_from_node(node)

    def update_balance(self, user: User):
        from app import Application
        session = Application.database.get_session()
        with session:
            result: Record = session.write_transaction(
                self.update_user_balance_transaction,
                balance=user.balance,
                user_id=user.id,
            )

    @staticmethod
    def get_users(cursor: int, limit: 50) -> Iterable[User]:
        raise NotImplementedError()

    def create_if_not_exist(self, username: str, email: str, password: str) -> User:
        from app import Application
        session = Application.database.get_session()
        with session:
            result: Record = session.write_transaction(
                self.create_user_transaction,
                username=username,
                email=email,
                password=password,
                created_on=datetime.datetime.now().isoformat()
            )
            node: Node = result.value()
            return self._parse_from_node(node)

    @staticmethod
    def _parse_from_node(node: Node) -> User:
        return User(
                id=node.id,
                username=node.get("username"),
                email=node.get("email"),
                password=node.get("password"),
                balance=node.get("balance"),
                created_on=datetime.datetime.fromisoformat(node.get('created_on'))
            )

    @staticmethod
    def create_user_transaction(tx: Transaction, username: str, email: str, password: str, created_on: str):
        query = "MERGE (p:User {username: $username}) " \
                "ON CREATE SET" \
                " p.email = $email," \
                " p.balance = 0," \
                " p.password = $password," \
                " p.created_on = $created_on " \
                "ON MATCH SET" \
                " p.lastAccessed = timestamp() " \
                "RETURN p "
        result = tx.run(query, username=username, email=email, password=password, created_on=created_on)
        return result.single()

    @staticmethod
    def update_user_balance_transaction(tx: Transaction, balance: int, user_id):
        query = "MATCH (u:User) WHERE ID(u) = $user_id SET u.balance = $balance"
        result = tx.run(query, balance=balance, user_id=user_id)
        return result.single()

