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
        buys: List[Decimal],
        sells: List[Decimal],
        dividends: List[Decimal],
        taxes: List[Decimal],
    ) -> Tuple[Money, Money, Money, Money]:
        """
        Input:
            buys - PLN paid for every buy/sell pair, always positive
            sells - PLN received for every buy/sell pair, always positive
            dividends - received dividends in PLN, always positive
            taxes - paid taxes in PLN, always zero or positive
        Return: (TotalProfit, TotalCost, TotalTax, TaxAlreadyPaid), all in PLN
            TotalIncome is money received from selling shares and from dividends
            TotalCost is money spent for buying shares
            TotalTax is TotalProfit * TAX_PERCENTAGE (as of 23.01.2021 - 19%). Can be >= 0.
            TaxAlreadyPaid is sum of Dividend taxes and Freestanding taxes listed in report so already deducted from trader's account.
        """

        total_income = Money("0", "PLN")
        total_income += sum(sells)
        total_income += sum(dividends)

        total_cost = Money("0", "PLN")
        total_cost += sum(buys)

        tax_already_paid = Money("0", "PLN")
        tax_already_paid += sum(taxes)

        total_profit = total_income - total_cost
        total_tax = self._calc_tax(total_profit)
        return (total_income, total_cost, total_tax, tax_already_paid)

    def _calc_tax(self, profit: Money) -> Money:
        if profit.amount < 0:
            return Money("0", "PLN")

        return profit * self._tax_percentage / 100
