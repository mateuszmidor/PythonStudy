from decimal import Decimal
from typing import Union
from money import Money
from dataclasses import dataclass


def PLN(amount: Union[Decimal, int]) -> Money:
    return Money(amount, "PLN")


@dataclass(frozen=True)
class TaxDeclarationNumbers:
    """
    Note: PIT38 tax declaration has separate fields for shares income and dividends income.
    This means loss on shares won't zero-out tax from dividends.
    """

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