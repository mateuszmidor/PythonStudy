import datetime
from money import Money
from decimal import Decimal


class ExchangeItem:
    def __init__(self, exchange_from: Money, exchange_to: Money, date: datetime.date, transaction_id: int):
        self.exchange_from = exchange_from
        self.exchange_to = exchange_to
        self.date = date
        self.transaction_id = transaction_id
