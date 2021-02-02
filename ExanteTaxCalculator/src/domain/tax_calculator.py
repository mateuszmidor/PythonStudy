from money import Money
from typing import List, Tuple
from datetime import datetime
from decimal import Decimal
from src.domain.currency import Currency


class TaxCalculator:
    def __init__(self, tax_percentage: Decimal) -> None:
        self._tax_percentage = tax_percentage

    def calc_profit_tax(
        self,
        trades: List[Decimal],
        dividends: List[Decimal],
        taxes: List[Decimal],
    ) -> Tuple[Money, Money, Money]:
        """
        Input:
            trades outcomes, positive or negative depending how did the trade go
            dividends, always positive
            taxes, always zero or positive
        Return: (TotalProfit, TotalTax, TaxAlreadyPaid), all in PLN
            TotalProfit is before deducting tax. Can be negative if transactions resulted in a loss.
            TotalTax is TotalProfit * TAX_PERCENTAGE (as of 23.01.2021 - 19%). Can be >= 0.
            TaxAlreadyPaid is sum of Dividend taxes and Freestanding taxes listed in report so already deducted from trader's account.
        """

        total_profit = Money("0", "PLN")
        total_profit += sum(trades)
        total_profit += sum(dividends)

        tax_already_paid = Money("0", "PLN")
        tax_already_paid += sum(taxes)

        total_tax = self._calc_tax(total_profit)
        return (total_profit, total_tax, tax_already_paid)

    def _calc_tax(self, profit: Money) -> Money:
        if profit.amount < 0:
            return Money("0", "PLN")

        return profit * self._tax_percentage / 100
