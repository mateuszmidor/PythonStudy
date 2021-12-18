import unittest
from src.domain.stock_exchange import stock_exchange_by_short_name
from test.utils.capture_exception import capture_exception


class StockExchangeTest(unittest.TestCase):
    def test_correctly_recognize_stock_exchange_country(self):
        # given
        cases = {
            "LSE": "Wielka Brytania",
            "LSEAIM": "Wielka Brytania",
            "LSEIOB": "Wielka Brytania",
            "AMEX": "Stany Zjednoczone",
            "ARCA": "Stany Zjednoczone",
            "NYSE": "Stany Zjednoczone",
            "NASDAQ": "Stany Zjednoczone",
            "HKEX": "Chiny",
            "SGX": "Singapur",
            "TMX": "Kanada",
            "XETRA": "Niemcy",
            "WSE": "Polska",
        }

        for short_name, expected_country in cases.items():
            # when
            actual_country = stock_exchange_by_short_name(short_name).country

            # then
            self.assertEqual(actual_country, expected_country, f"Incorrect country for stock exchange '{short_name}'")

    def test_unknown_exchange_raises_error(self):
        # when
        e = capture_exception(stock_exchange_by_short_name, "KONGO")

        # then
        self.assertIsInstance(e, ValueError)
