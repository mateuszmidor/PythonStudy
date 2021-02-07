from decimal import Decimal
from money import Money

from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN


class ProfitPLN:
    """ Note: Profit can also be negative if transaction resulted in loss of money """

    def __init__(self, source: BuySellPairPLN, paid, received: Decimal) -> None:
        self._source = source
        self._paid = Money(paid, "PLN")
        self._received = Money(received, "PLN")
        # profit net = received - paid

    @property
    def paid(self) -> Money:
        return self._paid

    @property
    def received(self) -> Money:
        return self._received

    # @property
    # def profit(self) -> Money:
    #     return self._profit

    @property
    def source(self) -> BuySellPairPLN:
        return self._source


ProfitItem = ProfitPLN
