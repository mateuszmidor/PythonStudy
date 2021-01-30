import datetime
from money import Money
from decimal import Decimal
from dataclasses import dataclass


@dataclass(frozen=True)
class ExchangeItem:
    exchange_from: Money
    exchange_to: Money
    # common transaction item data
    date: datetime.date = datetime.date(1970, 1, 1)
    transaction_id: int = 0
