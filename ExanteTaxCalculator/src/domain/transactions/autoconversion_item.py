from datetime import datetime
from money import Money
from dataclasses import dataclass


@dataclass(frozen=True)
class AutoConversionItem:
    conversion_from: Money
    conversion_to: Money
    # common transaction item data
    date: datetime = datetime(1970, 1, 1)
    transaction_id: int = 0
