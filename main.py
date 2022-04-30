import logging
import sys

from fastapi import FastAPI

# from api.v1.api import api_v1_router
from app import Application

from pydantic.tools import lru_cache

import config

formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s')
app = FastAPI(openapi_url="/api/v1/openapi.json", docs_url="/api/v1/swagger")

Application.fastapi_app = app
Application.init_routes()

logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s', level=logging.INFO,
                    datefmt='%m.%d.%Y %I:%M:%S')


@lru_cache()
def get_settings():
    return config.Settings()


@app.on_event("startup")
async def startup_event():
    Application.init_db_backend()
