import time
from typing import List, Iterable

from psycopg2.extras import execute_values


from core.impl_postgresql.database import SemaphoredThreadedConnectionPool
from core.models.place import Place
from core.models.user import User
from core.service_interfaces.places_service import PlacesService


class PostgreSQLPlacesService(PlacesService):

    QUERY_CLOSEST = "SELECT id, name, address, source_id, ST_X(location::geometry), ST_Y(location::geometry), st_distance(places.location, st_makepoint(%(lon)s, %(lat)s)) as pdistance" \
                    " FROM places WHERE ST_DWithin(places.location, st_makepoint(%(lon)s, %(lat)s), 1000) ORDER BY pdistance LIMIT %(limit)s;"

    """"""

    def get_closest_respect_advertising(self, lat: float, long: float, limit: int) -> Iterable[Place]:
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()

        connection = None
        try:
            connection = pool.getconn()
            before = time.time()
            with connection.cursor() as cursor:
                cursor.execute(self.QUERY_CLOSEST, {'lat': lat, 'lon': long, 'limit': limit})
                result = cursor.fetchall()
            estimated = "%.5f" % (time.time() - before)
            print(f"get_closest_respect_advertising took {estimated}s (Using {Application.database.name})")

        finally:
            if connection:
                pool.putconn(connection)


    def get_recommended(self, user: User, limit: int) -> Iterable[Place]:
        ...

    def batch_upsert(self, places: List[Place]):
        from app import Application
        pool: SemaphoredThreadedConnectionPool = Application.database.get_pool()
        connection = None
        argslist = []
        for p in places:
            argslist.append((p.source_id, p.name, p.address, p.image_url, p.longitude, p.latitude))
        try:
            connection = pool.getconn()
            with connection.cursor() as cursor:

                execute_values(cur=cursor,
                               sql="INSERT INTO places (source_id, name, address, image_url, location) VALUES %s "
                                   "ON CONFLICT (source_id) "
                                   "  DO UPDATE SET"
                                   "    name = EXCLUDED.name,"
                                   "    address = EXCLUDED.address,"
                                   "    image_url = EXCLUDED.image_url,"
                                   "    location = EXCLUDED.location,"
                                   "    last_updated_on = NOW() "
                                   "RETURNING id, source_id;",
                               argslist=argslist,
                               template='(%s, %s, %s, %s, st_makepoint(%s, %s))'
                               )
                result = cursor.fetchall()
                print("PSQL bulk upsert returning", result)
                connection.commit()

        finally:
            if connection:
                pool.putconn(connection)

    def drop_data(self):
        pass