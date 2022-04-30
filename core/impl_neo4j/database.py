import logging

import neo4j

from config import Settings
from core.database import DatabaseBackend


logger = logging.getLogger(__name__)


class Neo4jDatabaseBackend(DatabaseBackend):

    def __init__(self, name: str, settings: Settings):
        super().__init__(name)
        uri = f"neo4j://{settings.NEO4J_HOST}:{settings.NEO4J_PORT}"
        self.neo4j_driver: neo4j.Neo4jDriver = neo4j.GraphDatabase.driver(
            uri,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASS),
            encrypted=False,
            max_connection_pool_size=50,
        )
        # self.neo4j_driver.verify_connectivity()

    def get_session(self):
        return self.neo4j_driver.session()

    def get_pool(self):
        return self.neo4j_driver

    def create_schema(self):
        with self.neo4j_driver.session() as session:

            # places constraints
            session.run("CREATE CONSTRAINT place_source_id_uniqueness IF NOT EXISTS"
                        " FOR (place:Place) REQUIRE place.source_id IS UNIQUE")

            # places spatial index
            session.run("CREATE INDEX node_index_name IF NOT EXISTS FOR (p:Place) ON (p.location)")

            # user constraints
            session.run("CREATE CONSTRAINT user_email_uniqueness IF NOT EXISTS"
                        " FOR (user:User) REQUIRE user.email IS UNIQUE")
            session.run("CREATE CONSTRAINT user_email_existence IF NOT EXISTS"
                        " FOR (user:User) REQUIRE user.email IS NOT NULL")
            session.run("CREATE CONSTRAINT user_username_uniqueness IF NOT EXISTS"
                        " FOR (user:User) REQUIRE user.username IS UNIQUE")
            session.run("CREATE CONSTRAINT user_username_existence IF NOT EXISTS"
                        " FOR (user:User) REQUIRE user.username IS NOT NULL")
            session.run("CREATE CONSTRAINT user_password_existence IF NOT EXISTS"
                        " FOR (user:User) REQUIRE user.password IS NOT NULL")
            session.run("CREATE CONSTRAINT user_balance_existence IF NOT EXISTS"
                        " FOR (user:User) REQUIRE user.balance IS NOT NULL")
            session.run("CREATE CONSTRAINT user_created_on_existence IF NOT EXISTS"
                        " FOR (user:User) REQUIRE user.created_on IS NOT NULL")

            # product name NOT NULL
            session.run("CREATE CONSTRAINT products_name_existence IF NOT EXISTS"
                        " FOR (p:Product) REQUIRE p.name IS NOT NULL")
            # product name UNIQUE
            session.run("CREATE CONSTRAINT products_name_uniqueness IF NOT EXISTS"
                        " FOR (p:Product) REQUIRE p.name IS UNIQUE")
            # product description NOT NULL
            session.run("CREATE CONSTRAINT products_description_existence IF NOT EXISTS"
                        " FOR (p:Product) REQUIRE p.description IS NOT NULL")

            result = session.run("SHOW CONSTRAINTS")
            for v in result.values():
                print(v)
