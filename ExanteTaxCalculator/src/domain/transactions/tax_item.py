from datetime import datetime
from money import Money
from decimal import Decimal
from dataclasses import dataclass


@dataclass(frozen=True)
class TaxItem:
    paid_tax: Money
    # common transaction item data
    date: datetime = datetime(1970, 1, 1)
    transaction_id: int = 0
    comment: str = ""
