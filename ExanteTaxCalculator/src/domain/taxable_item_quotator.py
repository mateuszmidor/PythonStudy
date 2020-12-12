import datetime
from money import Money
from decimal import Decimal
from typing import List, Tuple, Optional, Protocol

from src.domain.errors import NoQuotesAvailableError
from src.domain.currency import Currency
from src.domain.taxable_item import TaxableItem
from src.domain.taxable_item_pln_quoted import TaxableItemPLNQuoted

class QuotesProviderProtocol(Protocol):
    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        pass


class TaxableItemPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotes_provider = quotes_provider

    def quote(self, item: TaxableItem) -> TaxableItemPLNQuoted:
        buy_quote_pln, buy_quotation_date = self._get_quote_for_working_day_before(item.buy_paid.currency, item.buy_date)
        buy_commission_quote_pln, _ = self._get_quote_for_working_day_before(item.buy_commission.currency, item.buy_date)
        buy_paid_pln = item.buy_paid.amount * buy_quote_pln
        buy_commission_pln = item.buy_commission.amount * buy_commission_quote_pln

        sell_quote_pln, sell_quotation_date = self._get_quote_for_working_day_before(item.sell_received.currency, item.sell_date)
        sell_commission_quote_pln, _ = self._get_quote_for_working_day_before(item.sell_commission.currency, item.sell_date)
        sell_received_pln = item.sell_received.amount * sell_quote_pln
        sell_commission_pln = item.sell_commission.amount * sell_commission_quote_pln

        quoted = TaxableItemPLNQuoted.from_taxable_item(item, 
                    buy_quotation_date, buy_paid_pln, buy_commission_pln,
                    sell_quotation_date, sell_received_pln, sell_commission_pln)
        return quoted


    def _get_quote_for_working_day_before(self, currency: str, date: datetime.date) -> Tuple[Decimal, datetime.date]:
        ONE_DAY = datetime.timedelta(days = 1)
        day_before = date - ONE_DAY
        quotation_day = day_before

        for _ in range(7): # look for quote up to 7 days back
            quote = self._quotes_provider.get_average_pln_for_day(Currency(currency), quotation_day)
            if quote is not None:
                return (quote, quotation_day)
            quotation_day -= ONE_DAY

        raise NoQuotesAvailableError(f"No PLN quotes available for {currency} in dates {quotation_day} - {day_before}")
