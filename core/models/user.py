import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: Optional[int]
    email: EmailStr
    username: str
    password: str
    balance: float
    created_on: datetime.datetime
    last_login: Optional[datetime.datetime]

