from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl
from pydantic.types import constr


class Sources(Enum):
    YANDEX = 0
    GOOGLE = 1


class Place(BaseModel):

    id: Optional[int]
    name: constr(max_length=128)
    address: constr(max_length=256)
    image_url: Optional[HttpUrl]
    longitude: float
    latitude: float
    source_id: Optional[str]
    last_updated_on: Optional[datetime]

    distance: Optional[int]
