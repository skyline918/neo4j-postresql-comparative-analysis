from multiprocessing import Semaphore
from typing import Optional

from psycopg2.extensions import connection as pg_connection
from psycopg2.pool import ThreadedConnectionPool

from config import Settings
from core.database import DatabaseBackend


class SemaphoredThreadedConnectionPool(ThreadedConnectionPool):
    def __init__(self, minconn, maxconn, *args, **kwargs):
        self._semaphore = Semaphore(maxconn)
        super().__init__(minconn, maxconn, *args, **kwargs)

    def getconn(self, *args, **kwargs) -> pg_connection:
        self._semaphore.acquire()
        return super().getconn(*args, **kwargs)

    def putconn(self, *args, **kwargs) -> None:
        super().putconn(*args, **kwargs)
        self._semaphore.release()


class PostgreSQLDatabaseBackend(DatabaseBackend):
    """
    for implementation part:
     - pool is not waiting if exhausted
     - no context manager (with keyword): handle pool manually
    """

    def __init__(self, name: str, settings: Settings):
        super().__init__(name)
        self.name = name
        self.psycopg2_pool = None

        self.psycopg2_pool = SemaphoredThreadedConnectionPool(
            minconn=1,
            maxconn=50,
            host=settings.POSTGRESQL_HOST,
            port=settings.POSTGRESQL_PORT,
            database=settings.POSTGRESQL_DB,
            user=settings.POSTGRESQL_USER,
            password=settings.POSTGRESQL_PASS,
        )
        # verify connectivity
        con: Optional[pg_connection] = None
        try:
            con = self.psycopg2_pool.getconn()
        finally:
            if con:
                self.psycopg2_pool.putconn(conn=con)

    def create_schema(self):
        con = None
        try:
            con = self.psycopg2_pool.getconn()
            with con.cursor() as cursor:

                cursor.execute("CREATE TABLE IF NOT EXISTS users  ("
                               "  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
                               "  email VARCHAR ( 255 ) UNIQUE NOT NULL, "
                               "  username VARCHAR ( 16 ) UNIQUE NOT NULL, "
                               "  password VARCHAR ( 64 ) NOT NULL, "
                               "  balance INTEGER NOT NULL DEFAULT 0 CHECK(balance > 0), "
                               "  created_on TIMESTAMP NOT NULL, "
                               "  last_login TIMESTAMP );")

                cursor.execute("CREATE TABLE IF NOT EXISTS places  ("
                               "  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
                               "  name VARCHAR(255) NOT NULL, "
                               "  address VARCHAR(255) NOT NULL, "
                               "  image_url VARCHAR(512), "
                               "  location GEOGRAPHY(Point) NOT NULL, "
                               "  created_on TIMESTAMP NOT NULL DEFAULT NOW(), "
                               "  source_id VARCHAR(128) UNIQUE NOT NULL, "
                               "  last_updated_on TIMESTAMP DEFAULT NOW()"
                               ");")
                cursor.execute("CREATE TABLE IF NOT EXISTS products ("
                               "  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
                               "  name VARCHAR(64) UNIQUE NOT NULL, "
                               "  description VARCHAR(255) NOT NULL, "
                               "  price INT CHECK (price >= 0)"
                               ");")
                cursor.execute("CREATE TABLE IF NOT EXISTS active_products ("
                               "  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
                               "  user_id BIGINT NOT NULL, "
                               "  product_id BIGINT NOT NULL, "
                               "  UNIQUE (user_id, product_id),"
                               "  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,"
                               "  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE"
                               ");")

                cursor.execute(
                    "CREATE OR REPLACE FUNCTION ensure_active_products_total() RETURNS trigger LANGUAGE plpgsql AS "
                    "$$BEGIN "
                    "IF (SELECT COUNT(id) FROM active_products WHERE user_id = NEW.user_id) > 3"
                    " THEN RAISE EXCEPTION '3 active products allowed maximum'; "
                    "END IF; "
                    "RETURN OLD;"
                    "END;$$;")
                cursor.execute("CREATE CONSTRAINT TRIGGER total_active_products"
                               " AFTER INSERT OR UPDATE ON active_products"
                               " NOT DEFERRABLE "
                               "FOR EACH ROW EXECUTE PROCEDURE ensure_active_products_total();")

                cursor.execute("CREATE INDEX places_location_gist_index ON places USING GIST (location);")

                con.commit()
        finally:
            if con:
                self.psycopg2_pool.putconn(con)

    def get_session(self):
        pass

    def get_pool(self):
        return self.psycopg2_pool


