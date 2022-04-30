import logging
import time
from typing import Iterable, List

import neo4j
from neo4j import Transaction, Result
from neo4j.graph import Node
from neo4j.spatial import Point
from neo4j.time import DateTime

from app import Application
from core.models.place import Place
from core.service_interfaces.places_service import PlacesService

logger = logging.getLogger()


class Neo4jPlacesService(PlacesService):

    CLOSEST_PLACES_QUERY = "MATCH (p:Place) RETURN p, point.distance(p.location, point({latitude: $lat, longitude: $lon})) ORDER BY point.distance(p.location, point({latitude: $lat, longitude: $lon})) ASCENDING LIMIT 50;"

    @staticmethod
    def parse_result(result: Result) -> List[Place]:
        places = []
        for v in result.values():
            node: Node = v[0]
            distance = v[1]
            pid = node.id
            address = node.get('address')
            name = node.get('name')
            point: Point = node.get('location')
            last_updated_on: DateTime = node.get('last_updated_on')
            places.append(Place(
                id=pid,
                address=address,
                name=name,
                last_updated_on=last_updated_on.iso_format(),
                longitude=point[0],
                latitude=point[1],
                distance=distance
            ))
        return places

    # noinspection PyProtectedMember
    def get_closest_respect_advertising(self, lat: float, long: float, limit: int) -> Iterable[Place]:

        session: neo4j.Session = Application.database.get_session()
        if not session._connection:
            # Do not estimate DB connection time, only raw query
            session._connect(None)
        with session:
            before = time.time()
            result: Result = session.run(query=Neo4jPlacesService.CLOSEST_PLACES_QUERY, lat=lat, lon=long)
            places: List[Place] = Neo4jPlacesService.parse_result(result)
            estimated = "%.5f" % (time.time() - before)
            print(f"get_closest_respect_advertising took {estimated}s (Using {Application.database.name})")

        return places

    def drop_data(self):
        session: neo4j.Session = Application.database.get_session()
        with session:
            session.run("MATCH (a:Place) DELETE a\n")

    @staticmethod
    def _batch_upsert_transaction(tx: Transaction, places: List[Place]):
        query = 'UNWIND $places AS place \n' \
                'MERGE (p:Place {source_id: place.source_id}) \n' \
                'ON CREATE \n' \
                '  SET\n' \
                '    p.name = place.name, \n' \
                '    p.address = place.address, \n' \
                '    p.image_url = place.image_url, \n' \
                '    p.location = point({latitude:place.latitude, longitude:place.longitude}), \n' \
                '    p.last_updated_on = datetime() \n' \
                'ON MATCH \n' \
                '  SET\n' \
                '    p.name = place.name, \n' \
                '    p.address = place.address, \n' \
                '    p.image_url = place.image_url, \n' \
                '    p.location = point({latitude:place.latitude, longitude:place.longitude}), \n' \
                '    p.last_updated_on = datetime() \n' \
                'RETURN ID(p), p.source_id'

        places_json = list(map(lambda p: p.dict(), places))
        logger.info("Upserting %s places...", len(places))

        start_time = time.time()
        result = tx.run(query, places=places_json)
        values = result.values()
        logger.info("Done. (%s seconds)", (time.time() - start_time))

        print("Result:", values)

    def batch_upsert(self, places: List[Place]):
        session: neo4j.Session = Application.database.get_session()
        with session:
            session.write_transaction(Neo4jPlacesService._batch_upsert_transaction, places)
