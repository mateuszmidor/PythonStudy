import datetime
from money import Money
from decimal import Decimal
from dataclasses import dataclass


@dataclass(frozen=True)
class AutoConversionItem:
    """
    Buy transaction entails autoconversions if the needed currency is not currently in the wallet.
    There can be 2 separate autoconversions: for the trade itself and for commission
    """

    conversion_from: Money
    conversion_to: Money
    # common transaction item data
    date: datetime.date = datetime.date(1970, 1, 1)
    transaction_id: int = 0
