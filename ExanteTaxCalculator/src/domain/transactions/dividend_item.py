from datetime import datetime
from money import Money
from decimal import Decimal
from dataclasses import dataclass, field
from typing import List, Optional

from src.domain.transactions.autoconversion_item import AutoConversionItem
from src.domain.transactions.tax_item import TaxItem


@dataclass(frozen=True)
class DividendItem:
    """
    Dividend usually is followed by Tax, but sometimes tax comes much later.
    In that case paid_tax.amount == 0
    Dividend can also entail autoconversions eg from SGD to USD
    """

    received_dividend: Money
    paid_tax: Optional[TaxItem] = None
    autoconversions: List[AutoConversionItem] = field(default_factory=list)
    # common transaction item data
    date: datetime = datetime(1970, 1, 1)
    transaction_id: int = 0
    comment: str = ""
