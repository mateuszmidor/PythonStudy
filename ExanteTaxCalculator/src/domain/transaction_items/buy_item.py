import datetime

from money import Money
from decimal import Decimal


class BuyItem:
    def __init__(self, asset_name: str, amount: Decimal, paid: Money, commission: Money, date: datetime.date, transaction_id: int):
        # read-only
        self._asset_name = asset_name
        self._amount = amount
        self._paid = paid
        self._commission = commission
        self._date = date
        self._transaction_id = transaction_id

    @property
    def asset_name(self) -> str:
        return self._asset_name

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def paid(self) -> Money:
        return self._paid

    @property
    def commission(self) -> Money:
        return self._commission

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def transaction_id(self) -> int:
        return self._transaction_id
