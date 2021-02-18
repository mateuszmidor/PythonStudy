from datetime import date
from decimal import Decimal
from dataclasses import dataclass

from src.domain.trading.buy_sell_pair import BuySellPair


@dataclass(frozen=True)
class BuySellPairPLN:
    source: BuySellPair

    buy_pln_quotation_date: date
    buy_paid_pln: Decimal
    buy_commission_pln: Decimal

    sell_pln_quotation_date: date
    sell_received_pln: Decimal
    sell_commission_pln: Decimal

    def __post__init__(self) -> None:
        BuySellPairPLN._validate(self.buy_pln_quotation_date, self.sell_pln_quotation_date)

    @staticmethod
    def _validate(buy_pln_quotation_date, sell_pln_quotation_date: date) -> None:
        if buy_pln_quotation_date > sell_pln_quotation_date:
            raise ValueError(
                f"buy_pln_quotation_date must be before sell_pln_quotation_date, got: buy {buy_pln_quotation_date}, sell {sell_pln_quotation_date}"
            )
