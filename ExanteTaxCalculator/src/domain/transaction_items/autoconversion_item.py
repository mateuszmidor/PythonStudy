import datetime
from money import Money
from decimal import Decimal


class AutoConversionItem:
    def __init__(self, conversion_from: Money, conversion_to: Money, date: datetime.date, transaction_id: int):
        # read-only
        self._conversion_from = conversion_from
        self._conversion_to = conversion_to
        self._date = date
        self._transaction_id = transaction_id

    @property
    def conversion_from(self) -> Money:
        return self._conversion_from

    @property
    def conversion_to(self) -> Money:
        return self._conversion_to

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def transaction_id(self) -> int:
        return self._transaction_id
