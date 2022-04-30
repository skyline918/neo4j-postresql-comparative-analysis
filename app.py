import logging
import sys

from fastapi import FastAPI

from core.database import DatabaseBackend
from core.impl_neo4j.product_service import Neo4jProductService
from core.impl_postgresql.places_service import PostgreSQLPlacesService
from core.impl_postgresql.product_service import PostgreSQLProductService
from core.service_interfaces.places_service import PlacesService
from core.service_interfaces.product_service import ProductService
from core.service_interfaces.user_service import UserService


logger = logging.getLogger(__name__)


class Application:
    fastapi_app: FastAPI
    database: DatabaseBackend
    user_service: UserService
    places_service: PlacesService
    product_service: ProductService

    @staticmethod
    def init_routes():
        from api.v1.api import api_v1_router
        Application.fastapi_app.include_router(api_v1_router, prefix='/api/v1')

    @staticmethod
    def init_db_backend():
        from main import get_settings
        from core.impl_neo4j.database import Neo4jDatabaseBackend
        from core.impl_neo4j.places_service import Neo4jPlacesService
        from core.impl_neo4j.user_service import Neo4jUserService
        from core.impl_postgresql.database import PostgreSQLDatabaseBackend
        from core.impl_postgresql.user_service import PostgreSQLUserService

        settings = get_settings()
        logger.info("Using %s database backend", settings.DATABASE_BACKEND)
        if settings.DATABASE_BACKEND.lower() == settings.NEO4J.lower():
            Application.database = Neo4jDatabaseBackend(settings.NEO4J, settings)
            Application.user_service = Neo4jUserService()
            Application.places_service = Neo4jPlacesService()
            Application.product_service = Neo4jProductService()

        elif settings.DATABASE_BACKEND.lower() == settings.POSTGRESQL.lower():
            Application.database = PostgreSQLDatabaseBackend(settings.POSTGRESQL, settings)
            Application.user_service = PostgreSQLUserService()
            Application.places_service = PostgreSQLPlacesService()
            Application.product_service = PostgreSQLProductService()

        else:
            types = (settings.NEO4J, settings.POSTGRESQL)
            message: str = "Invalid database backend: %s. Available types are: %s" % (settings.DATABASE_BACKEND, types)
            sys.exit(message)
