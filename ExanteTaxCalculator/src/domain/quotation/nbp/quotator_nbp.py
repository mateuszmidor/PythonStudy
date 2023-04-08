import json
import logging
import datetime
from http import HTTPStatus
from typing import Optional, Callable, Tuple, Mapping, Any
from decimal import Decimal

from src.domain.currency import Currency
from src.domain.errors import QuotationError

# http://api.nbp.pl/#kursyWalut
# curl http://api.nbp.pl/api/exchangerates/rates/a/usd/last/30
# curl http://api.nbp.pl/api/exchangerates/rates/a/usd/2021-01-15


# curl http://api.nbp.pl/api/exchangerates/rates/a/usd/2021-01-16
# 404 NotFound - Not Found - Brak danych


UrlFetcher = Callable[[str], Tuple[str, HTTPStatus]]
""" 
UrlFetcher is abstraction over http.get(url).

input: url string
output: body string, HTTPStatus. 
Eg. ("Not Found", 404)
Doesn't raise http exception, returns error code

Below example implementation:

@cache
def url_fetch(url: str) -> Tuple[str, HTTPStatus]:
    try:
        r = requests.get(url)
        return r.text, HTTPStatus(r.status_code)
    except requests.exceptions.HTTPError as err:
        return str(err), err.response.status_code
"""


class QuotatorNBP:
    """
    Get average currency/PLN quotes from NBP.
    API: http://api.nbp.pl/#kursyWalut
    """

    URL = "http://api.nbp.pl/api/exchangerates/rates/a/{currency}/{date}"  # table A for averag prices, currency as USD, date as 2020-03-23

    def __init__(self, fetcher: UrlFetcher) -> None:
        self._fetcher = fetcher
        self._logger = logging.getLogger(__name__)

    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        """Implements QuotesProviderProtocol"""

        url = QuotatorNBP._make_url(currency.value, date)
        return self._read_average_pln(url)

    @staticmethod
    def _make_url(currency: str, date: datetime.date) -> str:
        nbp_date = date.strftime("%Y-%m-%d")
        return QuotatorNBP.URL.format(currency=currency, date=nbp_date)

    def _read_average_pln(self, url: str) -> Optional[Decimal]:
        try:
            body, code = self._fetcher(url)
        except Exception as e:
            raise QuotationError(f"Error fetching url {url}") from e

        if code != HTTPStatus.OK:
            self._log_http_not_ok(code, body, url)
            return None

        try:
            data = json.loads(body)
        except Exception as e:
            raise QuotationError(f"Invalid JSON received from NBP for URL: {body}, {url}") from e

        return QuotatorNBP._extract_average_pln(data)

    def _log_http_not_ok(self, code: int, body: str, url: str) -> None:
        # NOT_FOUND is expected normal situation for weekdays when there is no quotation available
        if code == HTTPStatus.NOT_FOUND:
            self._logger.info(f"HTTP status {code}: fetching {url}: {body} - probably public holiday")
        else:
            self._logger.error(f"HTTP status {code}: fetching {url}: {body}")

    @staticmethod
    def _extract_average_pln(data: Mapping[str, Any]) -> Decimal:
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
            return Decimal(data["rates"][0]["mid"])
        except Exception as e:
            raise QuotationError(f"Cannot extract rates[0].mid value from dict: {data}") from e
