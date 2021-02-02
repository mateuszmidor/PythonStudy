import json
import logging
from typing import Optional, Callable
from datetime import datetime
from decimal import Decimal

from src.domain.currency import Currency

# http://api.nbp.pl/#kursyWalut
# curl http://api.nbp.pl/api/exchangerates/rates/a/usd/last/30
# curl http://api.nbp.pl/api/exchangerates/rates/a/usd/2021-01-15


# curl http://api.nbp.pl/api/exchangerates/rates/a/usd/2021-01-16
# 404 NotFound - Not Found - Brak danych


UrlFetcher = Callable[[str], str]  # input: url string, output: body string


class QuotatorNBP:
    """
    Get average currency/PLN quotes from NBP.
    API: http://api.nbp.pl/#kursyWalut
    """

    URL = "http://api.nbp.pl/api/exchangerates/rates/a/{currency}/{date}"  # currency as USD, date as 2020-03-23

    def __init__(self, fetcher: UrlFetcher) -> None:
        self._fetcher = fetcher
        self._logger = logging.getLogger(__name__)

    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        """ Implements QuotesProviderProtocol """

        url = self._make_url(currency, date)
        try:
            return self._read_average_pln(url)
        except Exception as e:
            self._logger.error(e)
            return None

    def _make_url(self, currency: str, date: datetime.date) -> str:
        nbp_date = date.strftime("%Y-%m-%d")
        return QuotatorNBP.URL.format(currency=currency, date=nbp_date)

    def _read_average_pln(self, url: str) -> Decimal:
        # NBP single quotation date format:
        # {
        #     "table": "A",
        #     "currency": "dolar amerykański",
        #     "code": "USD",
        #     "rates": [
        #         {
        #         "no": "009/A/NBP/2021",
        #         "effectiveDate": "2021-01-15",
        #         "mid": 3.7466
        #         }
        #     ]
        # }
        try:
            body = self._fetcher(url)
        except Exception as e:
            raise ValueError(f"Failed fetching URL: {URL}") from e

        try:
            data = json.loads(body)
        except Exception as e:
            raise ValueError(f"Invalid JSON received from NBP for URL: {body}, {url}") from e

        try:
            return Decimal(data["rates"][0]["mid"])
        except Exception as e:
            raise ValueError(f"Cannot extract rates[0].mid value from dict: {data}") from e
