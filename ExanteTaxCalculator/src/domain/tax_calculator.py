from money import Money
from typing import List, Tuple
from datetime import datetime
from decimal import Decimal
from src.domain.currency import Currency
from src.domain.profit_item import ProfitItem


class TaxCalculator:
    def __init__(self, tax_percentage: int) -> None:
        self._tax_percentage = tax_percentage

    def calc_profit_tax(self, items: List[ProfitItem]) -> Tuple[Money, Money]:
        total_profit = Money("0", "PLN")
        for item in items:
            total_profit += item.profit

        total_tax = self._calc_tax(total_profit)
        return (total_profit, total_tax)

    def _calc_tax(self, profit: Money) -> Money:
        tax_base = profit if profit.amount > Decimal(0) else Money("0", "PLN")
        tax_amount = tax_base * self._tax_percentage / 100
        return tax_amount
