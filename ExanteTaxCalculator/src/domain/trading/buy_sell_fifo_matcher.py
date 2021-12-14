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
from src.domain.transactions.stock_split_item import StockSplitItem
from src.domain.transactions.corporate_action_item import CorporateActionItem
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

    def rename(self, new_name: str) -> None:
        """to support CORPORATE ACTION"""
        old = self._item
        self._item = BuyItem(
            asset_name=new_name,
            amount=old.amount,
            paid=old.paid,
            commission=old.commission,
            autoconversions=old.autoconversions,
            date=old.date,
            transaction_id=old.transaction_id,
        )

    def split(self, ratio: Decimal) -> None:
        """to support STOCK SPLIT, can be actual split eg. 100 -> 200 or merge eg. 200 -> 100"""
        new_asset_left = self.asset_left * ratio
        if new_asset_left != int(new_asset_left):  # fractional amount not allowed
            raise Exception(f"After stock split the amount left is fractional: {new_asset_left}")

        old = self._item
        self._item = BuyItem(
            asset_name=old.asset_name,
            amount=old.amount * ratio,
            paid=old.paid,
            commission=old.commission,
            autoconversions=old.autoconversions,
            date=old.date,
            transaction_id=old.transaction_id,
        )
        self.asset_left = Decimal(int(new_asset_left))

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

    def corporate_action(self, item: CorporateActionItem) -> None:
        for i in range(len(self._owned_items)):
            if self._owned_items[i].asset_name == item.from_share.symbol:
                print("renaming", item.from_share.symbol, " -> ", item.to_share.symbol)
                self._owned_items[i].rename(item.to_share.symbol)

        # below is just historical transaction data; don't update historical names
        # for i in range(len(self._buy_sell_matches)):
        #     if self._buy_sell_matches[i].buy.asset_name == item.from_share.symbol:
        #         self._buy_sell_matches[i].buy.asset_name = item.to_share.symbol
        #     if self._buy_sell_matches[i].sell.asset_name == item.from_share.symbol:
        #         self._buy_sell_matches[i].sell.asset_name = item.to_share.symbol

    def stock_split(self, item: StockSplitItem) -> None:
        ratio = item.to_share.amount / item.from_share.amount
        for i in range(len(self._owned_items)):
            if self._owned_items[i].asset_name == item.from_share.symbol:
                print("splitting", item.from_share.symbol, " x ", ratio)
                self._owned_items[i].split(ratio)

    @property
    def buy_sell_pairs(self) -> List[BuySellPair]:
        return copy.deepcopy(self._buy_sell_matches)

    def _validate_sell(self, item: SellItem) -> None:
        amount_available = self._get_asset_amount_in_wallet(item.asset_name)
        if item.amount > amount_available:
            raise InsufficientAssetError(
                f"Trying to sell more asset than available: want {item.amount}, available {amount_available} {item.asset_name}, id: {item.transaction_id}"
            )

    def _get_asset_amount_in_wallet(self, asset: str) -> Decimal:
        total = Decimal("0")
        for item in self._owned_items:
            if item.asset_name == asset:
                total += item.asset_left
        return total
