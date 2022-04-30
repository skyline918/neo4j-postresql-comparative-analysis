from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl
from pydantic.types import constr


class Company(BaseModel):

    id: Optional[int]
    name: constr(max_length=256)
    last_updated_on: Optional[datetime]
