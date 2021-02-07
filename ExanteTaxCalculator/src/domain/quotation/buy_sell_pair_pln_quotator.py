from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol
from src.domain.quotation.working_day_before_quotator import WorkingDayBeforeQuotator


class BuySellPairPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotator = WorkingDayBeforeQuotator(quotes_provider)

    def quote(self, item: BuySellPair) -> BuySellPairPLN:
        buy_quote_pln, buy_quotation_date = self._quotator.quote(item.buy.paid.currency, item.buy.date)
        buy_commission_quote_pln, _ = self._quotator.quote(item.buy.commission.currency, item.buy.date)
        buy_paid_pln = item.buy.paid.amount * buy_quote_pln
        buy_commission_pln = item.buy.commission.amount * buy_commission_quote_pln

        sell_quote_pln, sell_quotation_date = self._quotator.quote(item.sell.received.currency, item.sell.date)
        sell_commission_quote_pln, _ = self._quotator.quote(item.sell.commission.currency, item.sell.date)
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
