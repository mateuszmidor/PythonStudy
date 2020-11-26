import unittest
from src.domain.currency import Currency
from src.utils.capture_exception import capture_exception

class CurrencyTest(unittest.TestCase):
    def test_cant_create_currency_2_characters(self):
        # when
        e = capture_exception(Currency, "EU")

        # then
        self.assertIsInstance(e, ValueError)

    def test_cant_create_currency_4_characters(self):
        # when
        e = capture_exception(Currency, "EURO")

        # then
        self.assertIsInstance(e, ValueError)

    def test_cant_create_currency_lowercase(self):
        # when
        e = capture_exception(Currency, "eur")

        # then
        self.assertIsInstance(e, ValueError)

    def test_cant_create_currency_with_number(self):
        # when
        e = capture_exception(Currency, "EU1")

        # then
        self.assertIsInstance(e, ValueError)