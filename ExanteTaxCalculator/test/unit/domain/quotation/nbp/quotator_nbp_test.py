import unittest
import pytest
from http import HTTPStatus
from decimal import Decimal
from datetime import datetime
from unittest.mock import create_autospec

from src.domain.quotation.nbp.quotator_nbp import QuotatorNBP, UrlFetcher
from src.domain.errors import QuotationError

NOT_FOUND_404 = ("404 Not Found", HTTPStatus.NOT_FOUND)
SOCKET_ERROR = Exception("Network socket error")


class QuotatorNBPTest(unittest.TestCase):
    def test_correct_url_formed_for_currency_and_date(self) -> None:
        # given
        currency = "USD"
        date = datetime(2020, 5, 16)  # saturday, no quotes for weekend days, so return error 404
        expected_url = "http://api.nbp.pl/api/exchangerates/rates/a/{:s}/{:%Y-%m-%d}".format(currency, date)
        fetcher = create_autospec(UrlFetcher)
        fetcher.return_value = NOT_FOUND_404
        quotator = QuotatorNBP(fetcher)

        # when
        _ = quotator.get_average_pln_for_day(currency, date)

        # then
        fetcher.assert_called_with(expected_url)

    def test_http_404_response_returns_none(self) -> None:
        # given
        currency = "USD"
        date = datetime(2020, 5, 16)  # saturday, no quotes for weekend days
        fetcher = create_autospec(UrlFetcher)
        fetcher.return_value = NOT_FOUND_404
        quotator = QuotatorNBP(fetcher)

        # when
        pln_to_usd = quotator.get_average_pln_for_day(currency, date)

        # then
        assert pln_to_usd is None

    def test_invalid_response_throws_exception(self) -> None:
        # given
        # should be: "mid", not "middle"
        response_body = """
        {
            "table": "A",
            "currency": "dolar amerykański",
            "code": "USD",
            "rates": [
                {
                "no": "009/A/NBP/2021",
                "effectiveDate": "2020-05-15",
                "middle": 4.2135
                }
            ]
        }
        """
        currency = "USD"
        date = datetime(2020, 5, 15)  # friday
        fetcher = create_autospec(UrlFetcher)
        fetcher.return_value = (response_body, HTTPStatus.OK)
        quotator = QuotatorNBP(fetcher)

        # when - then
        with pytest.raises(QuotationError):
            _ = quotator.get_average_pln_for_day(currency, date)

    def test_infrastructur_exception_raises_exception(self) -> None:
        # given
        currency = "USD"
        date = datetime(2020, 5, 15)  # friday
        fetcher = create_autospec(UrlFetcher)
        fetcher.side_effects = SOCKET_ERROR
        quotator = QuotatorNBP(fetcher)

        # when - then
        with pytest.raises(QuotationError):
            _ = quotator.get_average_pln_for_day(currency, date)

    def test_correct_response_returns_quotation(self) -> None:
        # given
        response_body = """
        {
            "table": "A",
            "currency": "dolar amerykański",
            "code": "USD",
            "rates": [
                {
                "no": "009/A/NBP/2021",
                "effectiveDate": "2020-05-15",
                "mid": 4.2135
                }
            ]
        }
        """
        currency = "USD"
        date = datetime(2020, 5, 15)  # friday
        fetcher = create_autospec(UrlFetcher)
        fetcher.return_value = (response_body, HTTPStatus.OK)
        quotator = QuotatorNBP(fetcher)

        # when
        pln_to_usd = quotator.get_average_pln_for_day(currency, date)

        # then
        assert pln_to_usd == Decimal(4.2135)
