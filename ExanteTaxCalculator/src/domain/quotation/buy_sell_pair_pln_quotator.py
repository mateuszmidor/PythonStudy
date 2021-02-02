import datetime
from money import Money
from decimal import Decimal
from typing import List, Tuple, Optional

from src.domain.errors import NoQuotesAvailableError
from src.domain.currency import Currency
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol


class BuySellPairPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotes_provider = quotes_provider

    def quote(self, item: BuySellPair) -> BuySellPairPLN:
        buy_quote_pln, buy_quotation_date = self._get_quote_for_working_day_before(item.buy.paid.currency, item.buy.date)
        buy_commission_quote_pln, _ = self._get_quote_for_working_day_before(item.buy.commission.currency, item.buy.date)
        buy_paid_pln = item.buy.paid.amount * buy_quote_pln
        buy_commission_pln = item.buy.commission.amount * buy_commission_quote_pln

        sell_quote_pln, sell_quotation_date = self._get_quote_for_working_day_before(item.sell.received.currency, item.sell.date)
        sell_commission_quote_pln, _ = self._get_quote_for_working_day_before(item.sell.commission.currency, item.sell.date)
        sell_received_pln = item.sell.received.amount * sell_quote_pln
        sell_commission_pln = item.sell.commission.amount * sell_commission_quote_pln

        quoted = BuySellPairPLN(
            source=item,
            buy_pln_quotation_date=buy_quotation_date,
            buy_paid_pln=buy_paid_pln,
            buy_commission_pln=buy_commission_pln,
            sell_pln_quotation_date=sell_quotation_date,
            sell_received_pln=sell_received_pln,
            sell_commission_pln=sell_commission_pln,
        )
        return quoted

    def _get_quote_for_working_day_before(self, currency: str, date: datetime.date) -> Tuple[Decimal, datetime.date]:
        """ result: [currency/PLN ratio, quotation date] """

        ONE_DAY = datetime.timedelta(days=1)
        day_before = date - ONE_DAY
        quotation_day = day_before

        for _ in range(7):  # look for quote up to 7 days back
            quote = self._quotes_provider.get_average_pln_for_day(Currency(currency), quotation_day)
            if quote is not None:
                return (quote, quotation_day)
            quotation_day -= ONE_DAY

        raise NoQuotesAvailableError(f"No PLN quotes available for {currency} in dates {quotation_day} - {day_before}")
