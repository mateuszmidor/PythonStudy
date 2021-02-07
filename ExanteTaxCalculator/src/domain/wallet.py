import copy
from decimal import Decimal
from money import Money
from typing import Dict, Mapping, List
from collections import defaultdict
from src.domain.transactions import *
from src.domain.errors import InsufficientAssetError


class PrettyPrintDefaultDict(defaultdict):
    def __str__(self) -> str:
        format_item = lambda k, v: "{: <20}: {}".format(k, v)
        items = [format_item(k, v) for k, v in self.items() if v != 0]
        return "\n".join(items)


class Wallet:
    """ Wallet keeps track of assets, it is updated by buy/sell/fund/withdraw/exchange operations """

    def __init__(self, initial_assets: Mapping[str, Decimal] = {}):
        self._assets = PrettyPrintDefaultDict(Decimal, initial_assets)

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

    def autoconversion(self, item: AutoConversionItem) -> None:
        """ autoconversion if effectively the same as exchange """
        if item.conversion_from.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to autoconvert {item.conversion_from}, but no such asset in the wallet: {self._assets}")
        if item.conversion_from.amount > self._assets[item.conversion_from.currency]:
            raise InsufficientAssetError(f"Tried to autoconvert {item.conversion_from}, but only has {self._assets[item.conversion_from.currency]}")

        self._assets[item.conversion_from.currency] -= item.conversion_from.amount
        self._assets[item.conversion_to.currency] += item.conversion_to.amount

    def dividend(self, item: DividendItem) -> None:
        self._assets[item.received_dividend.currency] += item.received_dividend.amount
        self._assets[item.paid_tax.currency] -= item.paid_tax.amount

    def tax(self, item: TaxItem) -> None:
        if item.paid_tax.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to pay tax {item.paid_tax}, but no such currency in the wallet")
        if item.paid_tax.amount > self._assets[item.paid_tax.currency]:
            raise InsufficientAssetError(f"Tried to pay tax {item.paid_tax}, but only has {self._assets[item.paid_tax.currency]}")
        self._assets[item.paid_tax.currency] -= item.paid_tax.amount

    def corporate_action(self, item: CorporateActionItem) -> None:
        if item.from_share.symbol not in self._assets:
            raise InsufficientAssetError(f"Tried to corporate action from {item.from_share}, but no such share in the wallet")
        if item.from_share.amount > self._assets[item.from_share.symbol]:
            raise InsufficientAssetError(f"Tried to corporate action from {item.from_share}, but only has {self._assets[item.from_share.symbol]}")
        self._assets[item.from_share.symbol] -= item.from_share.amount
        self._assets[item.to_share.symbol] += item.to_share.amount

    def buy(self, item: BuyItem) -> None:
        for autoconversion in item.autoconversions:
            self.autoconversion(autoconversion)

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
