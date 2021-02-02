from decimal import Decimal
from money import Money

from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN


class ProfitPLN:
    """ Note: Profit can also be negative if transaction resulted in loss of money """

    def __init__(self, source: BuySellPairPLN, profit: Decimal) -> None:
        self._source = source
        self._profit = Money(profit, "PLN")

    @property
    def profit(self) -> Money:
        return self._profit

    @property
    def source(self) -> BuySellPairPLN:
        return self._source


ProfitItem = ProfitPLN
