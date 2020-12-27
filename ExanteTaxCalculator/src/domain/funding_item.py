import datetime
from money import Money
from decimal import Decimal


class FundingItem:
    def __init__(self, funding_amount: Money, date: datetime.date, transaction_id: int):
        self.funding_amount = funding_amount
        self.date = date
        self.transaction_id = transaction_id
