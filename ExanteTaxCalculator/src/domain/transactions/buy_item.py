from datetime import datetime
from typing import List
from money import Money
from decimal import Decimal
from dataclasses import dataclass, field

from src.domain.transactions.autoconversion_item import AutoConversionItem


@dataclass(frozen=True)
class BuyItem:
    """
    Buy transaction entails autoconversions if the needed currency is not currently in the wallet.
    There can be 2 separate autoconversions: for the trade itself and for commission
    """

    asset_name: str
    amount: Decimal
    paid: Money
    commission: Money
    autoconversions: List[AutoConversionItem] = field(default_factory=list)
    # common transaction item data
    date: datetime = datetime(1970, 1, 1)
    transaction_id: int = 0
