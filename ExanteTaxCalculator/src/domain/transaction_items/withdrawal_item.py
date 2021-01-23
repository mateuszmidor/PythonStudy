import datetime
from money import Money
from decimal import Decimal


class WithdrawalItem:
    def __init__(self, withdrawal_amount: Money, date: datetime.date, transaction_id: int):
        self.withdrawal_amount = withdrawal_amount
        self.date = date
        self.transaction_id = transaction_id
