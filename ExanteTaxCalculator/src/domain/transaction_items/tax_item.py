import datetime
from money import Money
from decimal import Decimal


class TaxItem:
    def __init__(self, paid_tax: Money, date: datetime.date, transaction_id: int):
        # read-only
        self._paid_tax = paid_tax
        self._date = date
        self._transaction_id = transaction_id

    @property
    def paid_tax(self) -> Money:
        return self._paid_tax

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def transaction_id(self) -> int:
        return self._transaction_id
