import datetime

from money import Money

class BuyItem:
   def __init__(self, asset_name : str, amount : int, paid : Money, commission : Money, date : datetime.date, transaction_id: int):
      self.asset_name = asset_name
      self.amount = amount
      self.paid = paid
      self.commission = commission
      self.date = date
      self.asset_left = amount # if some amount was sold
      self.transaction_id = transaction_id