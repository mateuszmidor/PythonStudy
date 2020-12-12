import datetime
from typing import Optional
from src.domain.buy_item import BuyItem
from src.domain.sell_item import SellItem
from money import Money
from decimal import Decimal 
from dataclasses import dataclass

@dataclass
class TaxableItem:
    # to be filled by Trader
    asset_name: str 

    buy_amount: int 
    buy_paid: Money
    buy_commission: Money
    buy_date: datetime.date 
    buy_transaction_id: int

    sell_amount: int 
    sell_received: Money 
    sell_commission: Money 
    sell_date: datetime.date
    sell_transaction_id: int

    def __post_init__(self) -> None:
        if self.buy_date > self.sell_date:
            raise ValueError(f"buy_date must be before sell_date, got: buy {self.buy_date}, sell {self.sell_date}")

        if self.buy_transaction_id > self.sell_transaction_id:
            raise ValueError(f"buy_transaction_id must be less than sell_transaction_id, got: buy {self.buy_transaction_id}, sell {self.sell_transaction_id}")

    @classmethod 
    def from_buy_sell_items(cls, buy_item: BuyItem, sell_item: SellItem):
        return cls(
            asset_name = buy_item.asset_name,
            buy_amount = buy_item.amount,
            buy_paid = buy_item.paid,
            buy_commission = buy_item.commission,
            buy_date = buy_item.date,
            buy_transaction_id = buy_item.transaction_id,
            sell_amount = sell_item.amount,
            sell_received = sell_item.received,
            sell_commission = sell_item.commission,
            sell_date = sell_item.date,
            sell_transaction_id = sell_item.transaction_id
        )

