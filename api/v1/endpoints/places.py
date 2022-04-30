from typing import List, Iterable

from fastapi import APIRouter
from starlette.responses import Response

from app import Application
from core.models.place import Place
from core.service_interfaces.places_service import PlacesService
from datasets.yandex_places_api import fetch_places, fetch_places_of_russia

router = APIRouter()


@router.get('/', response_model=List[Place])
async def get_nearest_places(latitude: float, longitude: float):

    service: PlacesService = Application.places_service
    places: Iterable[Place] = service.get_closest_respect_advertising(lat=latitude, long=longitude, limit=50)
    return places


@router.put('/yandex_fetching_task')
async def yandex_fetching_task(clear_db: bool = False):
    service: PlacesService = Application.places_service
    if clear_db:
        service.drop_data()
    places = fetch_places_of_russia()
    service.batch_upsert(places=places)
    return Response(status_code=200)
