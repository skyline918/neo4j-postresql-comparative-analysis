import logging
from time import sleep
from typing import List
from requests import Response, Session

from core.models.place import Place
from datasets.globals import YANDEX_MAPS_API_BASE_URL, TEXT_QUERIES, API_KEY, YANDEX_PLACES_MAX_PAGE, CITIES_MAP, \
    DEFAULT_SPAN

logger = logging.getLogger(__name__)

params = {
    'apikey': API_KEY,
    'text': "Кафе",
    'lang': 'ru_RU',
    'll': '55.967790,54.743060', #  latitude, longitude
    'spn': DEFAULT_SPAN,
    'results': YANDEX_PLACES_MAX_PAGE
}


def fetch_places(http_session: Session, ll, spn) -> List[Place]:
    result = []
    dupl_sources = []
    params['ll'] = ll
    params['spn'] = spn
    for text in TEXT_QUERIES:
        params['text'] = text

        response: Response = http_session.get(YANDEX_MAPS_API_BASE_URL, params=params)
        logger.info(" - Code [%s] for '%s'. Total places: %s", response.status_code, text, len(response.json()['features']))
        for r in response.json()['features']:
            source_id = r['properties']['CompanyMetaData']['id']
            if source_id in dupl_sources:
                continue

            dupl_sources.append(source_id)
            result.append(Place(
                name=r['properties']['name'],
                address=r['properties']['CompanyMetaData']['address'],
                image_url=None,
                longitude=r['geometry']['coordinates'][0],
                latitude=r['geometry']['coordinates'][1],
                source_id=r['properties']['CompanyMetaData']['id']
            ))
        sleep(2)

    return result


def fetch_places_of_russia() -> List[Place]:
    http_session = Session()
    result = []
    for city, location in CITIES_MAP:
        logger.info(f"Fetching places from %s", city)
        result.extend(fetch_places(http_session, ll=location, spn=DEFAULT_SPAN))
        # break
    return result
