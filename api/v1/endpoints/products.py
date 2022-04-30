from typing import Iterable

from fastapi import APIRouter
from starlette.responses import Response

from api.v1.schemas.product_payload import ProductPayload
from app import Application
from core.models.place import Place
from core.models.product import Product
from core.service_interfaces.product_service import ProductService

router = APIRouter()


@router.post('/purchase/{product}/from/{user}/')
async def purchase(user: int, product: int):

    service: ProductService = Application.product_service
    service.purchase(user_id=user, product_id=product)
    return Response(status_code=200)


@router.post('/', response_model=Product)
def create(product: ProductPayload):
    service: ProductService = Application.product_service
    product = service.create(
        description=product.description,
        name=product.name,
        price=product.price
    )
    return product
