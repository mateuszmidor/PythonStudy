from money import Money
from typing import List, Tuple, Union
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from src.domain.currency import Currency


def PLN(amount: Union[Decimal, int]) -> Money:
    return Money(amount, "PLN")


@dataclass(frozen=True)
class CalculationResult:
    """ Note: PIT38 tax declaration has separate fields for shares income and dividends income """

    tax_percentage_used: Decimal = Decimal(19)
    """ Tax percentage used in calculating this result """

    shares_total_income: Money = PLN(0)
    """
    TAX language: Przychód
    This is the total shares income: money received from all the sold shares, reduced by buy and sell commissions.
    Always >= 0 PLN
    """

    shares_total_cost: Money = PLN(0)
    """
    TAX language: Koszt uzyskania przychodu
    This is the total cost: money paid for bought shares.
    Always >= 0 PLN
    """

    shares_total_tax: Money = PLN(0)
    """
    TAX language: Podatek należny
    This is the total tax to be paid as a percentage of shares total profit (if profit above 0).
    Always >= 0 PLN
    """

    dividends_total_income: Money = PLN(0)
    """
    TAX language: Przychód
    This is the total dividends income: money received from all the dividends.
    Always >= 0 PLN
    """

    dividends_total_tax: Money = PLN(0)
    """
    TAX language: Zryczałtowany podatek obliczony od przychodów
    This is the total tax to be paid as a percentage of dividends total profit.
    Always >= 0 PLN
    """

    dividends_tax_already_paid: Money = PLN(0)
    """
    TAX form: Podatek zapłacony za granicą
    This is the tax that was already deducted by the broker (from dividends income).
    It reduces the dividends tax yet to be paid.
    Always >= 0 PLN
    """

    dividends_tax_yet_to_be_paid: Money = PLN(0)
    """
    TAX form: Różnica między zryczałtowanym podatkiem a podatkiem zapłaconym za granicą
    This is the tax from dividends that finally needs to be paid.
    Always >= 0 PLN
    """


class TaxCalculator:
    def __init__(self, tax_percentage: Decimal) -> None:
        self._tax_percentage = tax_percentage

    def calc_profit_tax(
        self,
        buys: List[Decimal],
        sells: List[Decimal],
        dividends: List[Decimal],
        taxes: List[Decimal],
    ) -> CalculationResult:
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
        dividends_tax_already_paid = Decimal(sum(taxes))
        dividends_total_tax = self._calc_tax(dividends_total_income)
        dividends_tax_yet_to_be_paid = max(dividends_total_tax - dividends_tax_already_paid, Decimal(0))

        return CalculationResult(
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
