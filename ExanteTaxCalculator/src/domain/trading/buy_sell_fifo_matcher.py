"""
Buy - Sell item matching for taxation purposes

Scenario1:
    Input:
        buy  10 PHYS for 1000
        sell 10 PHYS for 1000
    Output item:
        (buy, sell, actually_sold = 10)
    Profit:
        2000 * 10/10 - 1000 * 10/10 = 1000


Scenario2:
    Input:
        buy  20 PHYS for 1000
        sell 10 PHYS for 1000
    Output item:
        (buy, sell, actually_sold = 10)
    Profit:
        1000 * 10/10 - 2000 * 10/20 = 0

Scanario3:
    Input:
        buy  20 PHYS for 2000
        sell_1 10 PHYS for 1000
        sell_2 10 PHYS for 1000
    Output item:
        (buy, sell_1, actually_sold = 10)
        (buy, sell_2, actually_sold = 10)
    Profit:
        1000 * 10/10 - 2000 * 10/20 = 0
        1000 * 10/10 - 2000 * 10/20 = 0

Scanario4:
    Input:
        buy_1 15 PHYS for 1500
        buy_2 15 PHYS for 1500 
        sell_1 10 PHYS for 1000
        sell_2 10 PHYS for 1000
        sell_3 10 PHYS for 1000
    Output item:
        (buy_1, sell_1, actually_sold = 10)
        (buy_1, sell_2, actually_sold = 5)
        (buy_2, sell_2, actually_sold = 5)
        (buy_2, sell_3, actually_sold = 10)
    Profit:
        1000 * 10/10 - 1500 * 10/15 = 0
        1000 *  5/10 - 1500 *  5/15 = 0
        1000 *  5/10 - 1500 *  5/15 = 0
        1000 * 10/10 - 1500 * 10/15 = 0

Scenario5:
    Input:
        buy_1 10 PHYS for 1000
        buy_2 10 PHYS for 1000
        sell 20 PHYS for 2000
    Output item:
        (buy_1, sell, actually_sold = 10)
        (buy_2, sell, actually_sold = 10)
    Profit:
        2000 * 10/20 - 1000 * 10/10 = 0
        2000 * 10/20 - 1000 * 10/10 = 0

Scenario6:
    Input:
        buy_1 10 PHYS for 1000
        buy_2 10 PHYS for 1000
        buy_3 10 PHYS for 1000
        sell_1 15 PHYS for 1500
        sell_2 15 PHYS for 1500
    Output items:
        (buy_1, sell_1, actually_sold = 10)
        (buy_2, sell_1, actually_sold = 5)
        (buy_2, sell_2, actually_sold = 5)
        (buy_3, sell_2, actually_sold = 10)
    Protif:
        1500 * 10/15 - 1000 * 10/10 = 0
        1500 *  5/15 - 1000 * 5/10 = 0
        1500 *  5/15 - 1000 * 5/10 = 0
        1500 * 10/15 - 1000 * 10/10 = 0
"""

import copy
from typing import List
from decimal import Decimal
from src.domain.transactions.buy_item import BuyItem
from src.domain.transactions.sell_item import SellItem
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.errors import InsufficientAssetError


class OwnedItem:
    def __init__(self, buy_item: BuyItem):
        # read-only
        self._item = copy.deepcopy(buy_item)
        # read-write
        self.asset_left = buy_item.amount

    def can_sell(self, item: SellItem) -> bool:
        return self.asset_name == item.asset_name and self.asset_left > 0

    def sell(self, amount: Decimal) -> Decimal:
        assert amount > Decimal(0)
        amount_sold = min(amount, self.asset_left)
        self.asset_left -= amount_sold
        return amount_sold

    @property
    def asset_name(self) -> str:
        return self.item.asset_name

    @property
    def item(self) -> BuyItem:
        return copy.deepcopy(self._item)


class BuySellFIFOMatcher:
    """
    Match sell items with buy items in FIFO manner.
    This is necessary to correctly calculate income and income cost.
    """

    def __init__(self) -> None:
        self._buy_sell_matches: List[BuySellPair] = []
        self._owned_items: List[OwnedItem] = []

    def buy(self, item: BuyItem) -> None:
        self._owned_items.append(OwnedItem(item))

    def sell(self, item: SellItem) -> None:
        self._validate_sell(item)

        i = 0  # process buys from oldest to newest - FIFO manner
        amount_to_sell = item.amount
        while amount_to_sell > 0:
            owned_item = self._owned_items[i]
            if owned_item.can_sell(item):
                amount_sold = owned_item.sell(amount_to_sell)
                amount_to_sell -= amount_sold
                buy_sell_pair = BuySellPair(buy=owned_item.item, sell=item, amount_sold=amount_sold)
                self._buy_sell_matches.append(buy_sell_pair)
            i += 1

    @property
    def buy_sell_pairs(self) -> List[BuySellPair]:
        return copy.deepcopy(self._buy_sell_matches)

    def _validate_sell(self, item: SellItem) -> None:
        amount_available = self._get_asset_amount_in_wallet(item.asset_name)
        if item.amount > amount_available:
            raise InsufficientAssetError(
                f"Trying to sell more asset than available: want {item.amount}, available {amount_available} {item.asset_name}"
            )

    def _get_asset_amount_in_wallet(self, asset: str) -> Decimal:
        total = Decimal("0")
        for item in self._owned_items:
            if item.asset_name == asset:
                total += item.asset_left
        return total
