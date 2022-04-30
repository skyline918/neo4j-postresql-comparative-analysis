from typing import Optional

from pydantic import BaseModel, constr


class Product(BaseModel):
    id: Optional[int]
    name: constr(max_length=64)
    description: constr(max_length=255)
    price: int


class ActiveProduct(BaseModel):
    id: Optional[int]