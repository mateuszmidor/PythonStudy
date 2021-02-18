import unittest
from src.domain.currency import Currency
from test.utils.capture_exception import capture_exception


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

    def test_recognize_popular_currencies(self):
        # given
        currencies = ["EUR", "USD", "GBP", "CHF", "CAD", "AUD", "HKD", "JPY", "sgd", "nok", "cny"]

        for cur in currencies:
            # when
            is_currency = Currency.is_currency(cur)

            # then
            self.assertTrue(is_currency)

    def test_recognize_non_currencies(self):
        # given
        non_currencies = ["EU1", "USA", "GBC", "CHFa", "ECAD", "AOD"]

        for cur in non_currencies:
            # when
            is_currency = Currency.is_currency(cur)

            # then
            self.assertFalse(is_currency)