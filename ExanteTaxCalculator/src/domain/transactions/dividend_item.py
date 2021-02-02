from datetime import datetime
from money import Money
from decimal import Decimal
from dataclasses import dataclass


@dataclass(frozen=True)
class DividendItem:
    """
    Dividend usually is followed by Tax, but sometimes tax comes much later.
    In that case paid_tax.amount == 0
    """

    received_dividend: Money
    paid_tax: Money
    # common transaction item data
    date: datetime = datetime(1970, 1, 1)
    transaction_id: int = 0
    comment: str = ""
