import logging
import os
import threading
from typing import List
from unittest import TestCase

from starlette.testclient import TestClient

from app import Application

logger = logging.getLogger(__name__)
DB_BACKEND = os.getenv("DATABASE_BACKEND", "").upper()


class ConcurrencyTestCase(TestCase):

    def setUp(self) -> None:
        Application.init_db_backend()
        self.client = TestClient(Application.fastapi_app)

        name = "Test Product for Race Condition"
        self.product = Application.product_service.create_if_not_exist(name=name, description="", price=100)
        self.user = Application.user_service.create_if_not_exist(username="skyline", email="test@mail.ru", password="123")
        self.user.balance = 500
        Application.user_service.update_balance(user=self.user)

    @staticmethod
    def thread_function(user_id, product_id, errors: List[Exception]):
        try:
            Application.product_service.purchase(user_id, product_id)
        except Exception as err:
            errors.append(err)

    def test_race_condition(self):

        errors = []
        t1 = threading.Thread(target=ConcurrencyTestCase.thread_function, args=(self.user.id, self.product.id, errors))
        t2 = threading.Thread(target=ConcurrencyTestCase.thread_function, args=(self.user.id, self.product.id, errors))
        t3 = threading.Thread(target=ConcurrencyTestCase.thread_function, args=(self.user.id, self.product.id, errors))
        t4 = threading.Thread(target=ConcurrencyTestCase.thread_function, args=(self.user.id, self.product.id, errors))
        t5 = threading.Thread(target=ConcurrencyTestCase.thread_function, args=(self.user.id, self.product.id, errors))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()

        if len(errors) > 0:
            # capture exceptions from threads like a boss (no)
            raise errors[0]

        user = Application.user_service.get_by_id(user_id=self.user.id)
        self.assertEqual(0, user.balance, "Balance is not correct, most probably because of race condition")
