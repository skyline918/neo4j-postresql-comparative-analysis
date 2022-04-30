import os

from pydantic import BaseSettings


class Settings(BaseSettings):

    NEO4J = 'neo4j'
    NEO4J_HOST = os.environ.get("NEO4J_HOST", "localhost")
    NEO4J_PORT = os.environ.get("NEO4J_PORT", "7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASS = os.environ.get("NEO4J_PASS", "neo4j")

    POSTGRESQL = 'postgresql'
    POSTGRESQL_HOST = os.environ.get("POSTGRESQL_HOST", "localhost")
    POSTGRESQL_DB = os.environ.get("POSTGRESQL_DB", "postgres")
    POSTGRESQL_PORT = os.environ.get("POSTGRESQL_PORT", "5432")
    POSTGRESQL_USER = os.environ.get("POSTGRESQL_USER", "postgres")
    POSTGRESQL_PASS = os.environ.get("POSTGRESQL_PASS", "postgres")

    DATABASE_BACKEND = os.environ.get("DATABASE_BACKEND", "neo4j")
    # DATABASE_BACKEND = 'postgresql'

    class Config:
        env_file = ".env"
