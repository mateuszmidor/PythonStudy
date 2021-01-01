import copy
from typing import List
from decimal import Decimal
from src.domain.buy_item import BuyItem
from src.domain.sell_item import SellItem
from src.domain.taxable_item import TaxableItem
from src.domain.errors import InsufficientAssetError


class OwnedItem:
    def __init__(self, buy_item: BuyItem):
        # read-only
        self._buy_item = buy_item

        # read-write
        self.asset_left = self.buy_item.amount

    def can_sell(self, item: SellItem) -> bool:
        return self.asset_name == item.asset_name and self.asset_left > 0

    def sell(self, amount: Decimal) -> Decimal:
        amount_sold = min(amount, self.asset_left)
        self.asset_left -= amount_sold
        return amount_sold

    @property
    def asset_name(self) -> str:
        return self.buy_item.asset_name

    @property
    def buy_item(self) -> BuyItem:
        return copy.deepcopy(self._buy_item)


class Trader:
    def __init__(self) -> None:
        self._taxable_items: List[TaxableItem] = []
        self._owned_items: List[OwnedItem] = []

    def buy(self, item: BuyItem) -> None:
        self._owned_items.append(OwnedItem(item))

    def sell(self, item: SellItem) -> None:
        self._validate_sell(item)

        i = 0  # process trades from oldest to newest
        amount_to_sell = item.amount
        while amount_to_sell > 0:
            owned_item = self._owned_items[i]
            if owned_item.can_sell(item):
                amount_sold = owned_item.sell(amount_to_sell)
                amount_to_sell -= amount_sold

                sell_item = SellItem(
                    asset_name=item.asset_name,
                    amount=amount_sold,
                    received=item.received,
                    commission=item.commission,
                    date=item.date,
                    transaction_id=item.transaction_id,
                )
                taxable_item = TaxableItem.from_buy_sell_items(owned_item.buy_item, sell_item)
                self._taxable_items.append(taxable_item)
            i += 1

    @property
    def taxable_items(self) -> List[TaxableItem]:
        return copy.deepcopy(self._taxable_items)

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
