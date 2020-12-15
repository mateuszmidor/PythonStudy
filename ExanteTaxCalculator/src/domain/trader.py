from typing import List

from src.domain.currency_wallet import CurrencyWallet
from src.domain.buy_item import BuyItem
from src.domain.sell_item import SellItem
from src.domain.taxable_item import TaxableItem

import copy

class Trader:
    def __init__(self) -> None:
        self._taxable_items : List[TaxableItem] = []
        self._buy_items : List[BuyItem] = []

    def buy(self, item: BuyItem) -> None:
        self._buy_items.append(item)

    def sell(self, item: SellItem) -> None:
        amount_to_sell = item.amount
        amount_available = self._get_asset_amount_in_wallet(item.asset_name)

        if amount_to_sell > amount_available:
            raise ValueError(f"Trying to sell more than available asset: want {amount_to_sell}, available {amount_available} {item.asset_name}")

        i = 0 # process trades from oldest to newest 
        while amount_to_sell > 0:
            trade = self._buy_items[i]
            if trade.asset_name == item.asset_name and trade.asset_left > 0:
                amount_sold = min(amount_to_sell, trade.asset_left)
                assert amount_sold > 0 # should be no assets with zero amount on list
                trade.asset_left-= amount_sold
                amount_to_sell -= amount_sold

                sell_item = copy.deepcopy(item)
                sell_item.amount = amount_sold
                taxable_item = TaxableItem.from_buy_sell_items(trade, sell_item)
                self._taxable_items.append(taxable_item)
            i += 1

    def taxable_items(self):
        return copy.deepcopy(self._taxable_items)
        
    def _get_asset_amount_in_wallet(self, asset: str) -> int:
        total = 0
        for item in self._buy_items:
            if item.asset_name == asset:
                total += item.asset_left
        return total

