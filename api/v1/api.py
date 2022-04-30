from fastapi import APIRouter

from app import Application
from .endpoints import (
    users,
    products,
    places,
)

api_v1_router = APIRouter()
api_v1_router.include_router(users.router, prefix="/users")
api_v1_router.include_router(places.router, prefix="/places")
api_v1_router.include_router(products.router, prefix="/products")

