import datetime
from money import Money
from decimal import Decimal
from typing import List, Tuple, Optional

from src.domain.errors import NoQuotesAvailableError
from src.domain.currency import Currency
from src.domain.transactions.tax_item import TaxItem
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol


class TaxItemPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotes_provider = quotes_provider

    def quote(self, item: TaxItem) -> TaxItemPLN:
        tax_quote_pln, tax_quotation_date = self._get_quote_for_working_day_before(item.paid_tax.currency, item.date)
        paid_tax_pln = item.paid_tax.amount * tax_quote_pln

        quoted = TaxItemPLN(
            source=item,
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
