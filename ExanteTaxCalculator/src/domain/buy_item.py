import datetime

from money import Money

class BuyItem:
   def __init__(self, asset_name : str, amount : int, paid : Money, commision : Money, date : datetime.date):
      self.asset_name = asset_name
      self.amount = amount
      self.paid = paid
      self.commision = commision
      self.date = date
      self.asset_left = amount # if some amount was sold