import datetime
from src.domain.buy_item import BuyItem
from src.domain.sell_item import SellItem
from money import Money
from decimal import Decimal 

class TaxItem:
    def __init__(self, buy_item: BuyItem, sell_item: SellItem) -> None:
        self.buy_item = buy_item
        self.sell_item = sell_item

        # to be filled by Trader
        asset_name: str 

        buy_amount: int 
        buy_paid: Money
        buy_commission: Money
        buy_date: datetime.date 

        sell_amount: int 
        sell_received: Money 
        sell_commision: Money 
        sell_date: datetime.date

        # to be filled by TaxCalculator
        buy_pln_quotation_date: datetime.date
        buy_paid_pln: Decimal
        buy_commission_pln: Decimal

        sell_pln_quotation_date: datetime.date 
        sell_received_pln: Decimal 
        sell_commision_pln: Decimal

    @classmethod 
    def from_buy_sell_items(cls, buy_item: BuyItem, sell_item: SellItem):
        pass

