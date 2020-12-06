import datetime
from money import Money

class SellItem:
   def __init__(self, asset_name : str, amount : int, paid : Money, commision : Money, date : datetime.date):
      self.asset_name = asset_name
      self.amount = amount
      self.paid = paid
      self.commision = commision
      self.date = date