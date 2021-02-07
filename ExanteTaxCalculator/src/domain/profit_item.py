from decimal import Decimal
from money import Money

from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN


class ProfitPLN:
    """ Note: Profit can also be negative if transaction resulted in loss of money """

    def __init__(self, source: BuySellPairPLN, paid, received: Decimal) -> None:
        self._source = source
        self._paid = Money(paid, "PLN")
        self._received = Money(received, "PLN")

    @property
    def paid(self) -> Money:
        """ Paid money for buying shares in PLN """
        return self._paid

    @property
    def received(self) -> Money:
        """ Received money for selling shares in PLN """
        return self._received

    @property
    def source(self) -> BuySellPairPLN:
        return self._source


ProfitItem = ProfitPLN
