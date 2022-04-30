from typing import List

from fastapi import APIRouter

from core.models.user import User

router = APIRouter()


@router.get('/', response_model=List[User])
async def get_users() -> List[User]:
    return []
