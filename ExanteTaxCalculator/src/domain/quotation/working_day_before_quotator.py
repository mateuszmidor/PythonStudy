import datetime
from typing import Tuple
from decimal import Decimal

from src.domain.errors import NoQuotesAvailableError
from src.domain.currency import Currency
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol


class WorkingDayBeforeQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotes_provider = quotes_provider

    def quote(self, currency: str, date: datetime.datetime) -> Tuple[Decimal, datetime.date]:
        """ result: [currency/PLN ratio, quotation date] """

        curr = Currency(currency)
        date = datetime.date(date.year, date.month, date.day)  # only date, no time information is needed for quotation
        ONE_DAY = datetime.timedelta(days=1)
        day_before = date - ONE_DAY
        quotation_day = day_before

        for _ in range(7):  # look for quote up to 7 days back
            quote = self._quotes_provider.get_average_pln_for_day(curr, quotation_day)
            if quote is not None:
                return (quote, quotation_day)
            quotation_day -= ONE_DAY

        raise NoQuotesAvailableError(f"No PLN quotes available for {curr} in dates {quotation_day} - {day_before}")
