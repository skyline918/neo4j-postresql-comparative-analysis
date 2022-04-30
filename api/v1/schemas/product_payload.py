from pydantic import BaseModel, constr, conint


class ProductPayload(BaseModel):

    name: constr(max_length=64)
    description: constr(max_length=255)
    price: conint(gt=50, lt=10000)