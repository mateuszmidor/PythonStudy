import copy
from decimal import Decimal
from money import Money
from typing import Dict, Mapping
from collections import defaultdict
from src.domain.funding_item import FundingItem
from src.domain.withdrawal_item import WithdrawalItem
from src.domain.exchange_item import ExchangeItem
from src.domain.buy_item import BuyItem
from src.domain.sell_item import SellItem
from src.domain.errors import InsufficientAssetError


class Wallet:
    """ Wallet keeps track of assets amended by buy/sell/fund/withdraw/exchange operations """

    def __init__(self, initial_assets: Mapping[str, Decimal] = {}):
        self._assets = defaultdict(Decimal, initial_assets)

    def fund(self, item: FundingItem) -> None:
        self._assets[item.funding_amount.currency] += item.funding_amount.amount

    def withdraw(self, item: WithdrawalItem) -> None:
        if item.withdrawal_amount.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to withdraw {item.withdrawal_amount}, but no such asset in the wallet")
        if item.withdrawal_amount.amount > self._assets[item.withdrawal_amount.currency]:
            raise InsufficientAssetError(f"Tried to withdraw {item.withdrawal_amount}, but only has {self._assets[item.withdrawal_amount.currency]}")
        self._assets[item.withdrawal_amount.currency] -= item.withdrawal_amount.amount

    def exchange(self, item: ExchangeItem) -> None:
        if item.exchange_from.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to exchange {item.exchange_from}, but no such asset in the wallet: {self._assets}")
        if item.exchange_from.amount > self._assets[item.exchange_from.currency]:
            raise InsufficientAssetError(f"Tried to exchange {item.exchange_from}, but only has {self._assets[item.exchange_from.currency]}")

        self._assets[item.exchange_from.currency] -= item.exchange_from.amount
        self._assets[item.exchange_to.currency] += item.exchange_to.amount

    def buy(self, item: BuyItem) -> None:
        assets = self.assets
        assets[item.paid.currency] -= item.paid.amount
        assets[item.commission.currency] -= item.commission.amount
        if assets[item.paid.currency] < 0 or assets[item.commission.currency] < 0:
            raise InsufficientAssetError(f"Tried to buy {item.__dict__} but insufficient money")
        self._assets[item.asset_name] += item.amount
        self._assets[item.paid.currency] -= item.paid.amount
        self._assets[item.commission.currency] -= item.commission.amount

    def sell(self, item: SellItem) -> None:
        assets = self.assets
        assets[item.asset_name] -= item.amount
        assets[item.received.currency] += item.received.amount
        assets[item.commission.currency] -= item.commission.amount
        if assets[item.asset_name] < 0 or assets[item.commission.currency] < 0:
            raise InsufficientAssetError(f"Tried to sell {item.__dict__} but insufficient money/asset")
        self._assets[item.asset_name] -= item.amount
        self._assets[item.received.currency] += item.received.amount
        self._assets[item.commission.currency] -= item.commission.amount

    @property
    def assets(self) -> Dict[str, Decimal]:
        return copy.deepcopy(self._assets)

    # def get(self, currency: Currency) -> Decimal:
    #     return self._currencies[currency]

    # @property
    # def currencies(self) -> Dict[str, Decimal]:
    #     return copy.deepcopy(self._currencies)

    # def pay_out(self, m: Money):
    #     currency = Currency(m.currency)
    #     self._currencies[currency] -= m.amount
