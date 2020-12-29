from decimal import Decimal
from money import Money
from typing import Optional

from src.domain.taxable_item_pln_quoted import TaxableItemPLNQuoted

class ProfitPLN:
    def __init__(self, profit: Decimal, source_transaction_pair: Optional[TaxableItemPLNQuoted] = None) -> None:
        self.profit = Money(profit, "PLN")
        self.source_transaction_pair = source_transaction_pair

ProfitItem = ProfitPLN
