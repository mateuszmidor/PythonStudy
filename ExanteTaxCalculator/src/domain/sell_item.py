import datetime
from money import Money
from decimal import Decimal


class SellItem:
    def __init__(self, asset_name: str, amount: Decimal, received: Money, commission: Money, date: datetime.date, transaction_id: int):
        self.asset_name = asset_name
        self.amount = amount
        self.received = received
        self.commission = commission
        self.date = date
        self.transaction_id = transaction_id
