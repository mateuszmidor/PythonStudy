from money import Money
from typing import List, Tuple, Union
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from src.domain.tax_declaration.tax_declaration_numbers import TaxDeclarationNumbers


def PLN(amount: Union[Decimal, int]) -> Money:
    return Money(amount, "PLN")


class TaxDeclarationNumbersCalculator:
    def __init__(self, tax_percentage: Decimal) -> None:
        self._tax_percentage = tax_percentage

    def calc_tax_declaration_numbers(
        self,
        buys: List[Decimal],
        sells: List[Decimal],
        dividends: List[Decimal],
        dividend_taxes: List[Decimal],
    ) -> TaxDeclarationNumbers:
        """
        Input:
            buys - PLN paid for every buy/sell pair, always >= 0
            sells - PLN received for every buy/sell pair, always >= 0
            dividends - PLN received from dividends, always >= 0
            taxes - PLN paid for taxes, always >= 0
        """

        shares_total_income = Decimal(sum(sells))
        shares_total_cost = Decimal(sum(buys))
        shares_total_tax = self._calc_tax(shares_total_income - shares_total_cost)

        dividends_total_income = Decimal(sum(dividends))
        dividends_tax_already_paid = Decimal(sum(dividend_taxes))
        dividends_total_tax = self._calc_tax(dividends_total_income)
        dividends_tax_yet_to_be_paid = max(dividends_total_tax - dividends_tax_already_paid, Decimal(0))

        return TaxDeclarationNumbers(
            tax_percentage_used=self._tax_percentage,
            shares_total_income=PLN(shares_total_income),
            shares_total_cost=PLN(shares_total_cost),
            shares_total_tax=PLN(shares_total_tax),
            dividends_total_income=PLN(dividends_total_income),
            dividends_total_tax=PLN(dividends_total_tax),
            dividends_tax_already_paid=PLN(dividends_tax_already_paid),
            dividends_tax_yet_to_be_paid=PLN(dividends_tax_yet_to_be_paid),
        )

    def _calc_tax(self, profit: Decimal) -> Decimal:
        if profit < Decimal(0):
            return Decimal(0)

        return profit * self._tax_percentage / 100
