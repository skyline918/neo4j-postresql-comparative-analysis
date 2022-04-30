import logging
import time
from pprint import pprint
from unittest import TestCase
from urllib.parse import urlencode

from starlette.testclient import TestClient

from app import Application

logger = logging.getLogger(__name__)


class PlacesTest(TestCase):

    def setUp(self) -> None:
        Application.init_db_backend()
        self.client = TestClient(Application.fastapi_app)

    def tearDown(self) -> None:
        self.client = None

    def test_read_main(self):
        # б-р Ибрагимова, 37, Уфа, Респ. Башкортостан, 450000
        params = urlencode({
            'longitude': 55.967790,
            'latitude': 54.743060
        })
        response = self.client.get(f"/api/v1/places/?{params}")
        pprint(response.json())
        assert response.status_code == 200

    def test_purchase(self):
        product_id = 1
        user_id = 1
        response = self.client.post(f"/api/v1/products/purchase/{product_id}/users/{user_id}/")
