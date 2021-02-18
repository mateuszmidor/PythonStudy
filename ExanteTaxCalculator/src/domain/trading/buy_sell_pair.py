from copy import deepcopy
from decimal import Decimal
from dataclasses import dataclass
from src.domain.transactions.buy_item import BuyItem
from src.domain.transactions.sell_item import SellItem


@dataclass(frozen=True)
class BuySellPair:
    buy: BuyItem  # original unmodified buy item
    sell: SellItem  # that was matched with this original unmodified sell item
    amount_sold: Decimal  # no matter if this pair comes from buy 200,sell 100 or buy 100,sell 200, this is what is to be taxed

    def __post__init__(self) -> None:
        BuySellPair._validate(self.buy, self.sell, self.amount_sold)

    @staticmethod
    def _validate(buy: BuyItem, sell: SellItem, amount_sold: Decimal) -> None:
        if buy.date > sell.date:
            raise ValueError(f"buy.date must be before sell.date, got: buy {buy.date}, sell {sell.date}")

        if buy.transaction_id > sell.transaction_id:
            raise ValueError(f"buy.transaction_id must be less than sell.transaction_id:, got: buy {buy.transaction_id}, sell {sell.transaction_id}")

        if amount_sold > buy.amount:
            raise ValueError(f"amount_sold must be less/equal buy.amount, got: amount_sold {amount_sold}, buy.amount: {buy.amount}")

        if amount_sold > sell.amount:
            raise ValueError(f"amount_sold must be less/equal sell.amount, got: amount_sold {amount_sold}, sell.amount: {sell.amount}")
