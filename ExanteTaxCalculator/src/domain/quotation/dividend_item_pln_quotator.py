import datetime
from money import Money
from decimal import Decimal
from typing import List, Tuple, Optional

from src.domain.errors import NoQuotesAvailableError
from src.domain.currency import Currency
from src.domain.transactions.dividend_item import DividendItem
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol


class DividendItemPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotes_provider = quotes_provider

    def quote(self, item: DividendItem) -> DividendItemPLN:
        dividend_quote_pln, dividend_quotation_date = self._get_quote_for_working_day_before(item.received_dividend.currency, item.date)
        received_dividend_pln = item.received_dividend.amount * dividend_quote_pln

        tax_quote_pln, tax_quotation_date = self._get_quote_for_working_day_before(item.paid_tax.currency, item.date)
        paid_tax_pln = item.paid_tax.amount * tax_quote_pln

        quoted = DividendItemPLN(
            source=item,
            dividend_pln_quotation_date=dividend_quotation_date,
            received_dividend_pln=received_dividend_pln,
            tax_pln_quotation_date=tax_quotation_date,
            paid_tax_pln=paid_tax_pln,
        )

        return quoted

    def _get_quote_for_working_day_before(self, currency: str, date: datetime.date) -> Tuple[Decimal, datetime.date]:
        ONE_DAY = datetime.timedelta(days=1)
        day_before = date - ONE_DAY
        quotation_day = day_before

        for _ in range(7):  # look for quote up to 7 days back
            quote = self._quotes_provider.get_average_pln_for_day(Currency(currency), quotation_day)
            if quote is not None:
                return (quote, quotation_day)
            quotation_day -= ONE_DAY

        raise NoQuotesAvailableError(f"No PLN quotes available for {currency} in dates {quotation_day} - {day_before}")
