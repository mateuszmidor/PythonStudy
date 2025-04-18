import copy
from decimal import Decimal
from money import Money
from typing import Dict, Mapping, List
from collections import defaultdict
from src.domain.transactions import *
from src.domain.errors import InsufficientAssetError


class Wallet:
    """Wallet keeps track of assets, it is updated by buy/sell/fund/withdraw/exchange/tax/dividend/corporate_action/issuance_fee/stock_split operations"""

    def __init__(self, initial_assets: Mapping[str, Decimal] = {}):
        self._assets = defaultdict(Decimal, initial_assets)

    def fund(self, item: FundingItem) -> None:
        self._assets[item.funding_amount.currency] += item.funding_amount.amount

    def withdraw(self, item: WithdrawalItem) -> None:
        # check transaction possible
        if item.withdrawal_amount.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to withdraw {item.withdrawal_amount}, but no such asset in the wallet")
        if item.withdrawal_amount.amount > self._assets[item.withdrawal_amount.currency]:
            raise InsufficientAssetError(f"Tried to withdraw {item.withdrawal_amount}, but only has {self._assets[item.withdrawal_amount.currency]}")

        # apply transaction
        self._assets[item.withdrawal_amount.currency] -= item.withdrawal_amount.amount

    def exchange(self, item: ExchangeItem) -> None:
        # check transaction possible
        if item.exchange_from.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to exchange {item.exchange_from}, but no such asset in the wallet: {self._assets}")
        if item.exchange_from.amount > self._assets[item.exchange_from.currency]:
            raise InsufficientAssetError(f"Tried to exchange {item.exchange_from}, but only has {self._assets[item.exchange_from.currency]}")

        # apply transaction
        self._assets[item.exchange_from.currency] -= item.exchange_from.amount
        self._assets[item.exchange_to.currency] += item.exchange_to.amount

    # in 2023 it turned out that autoconversion can be a standalone transaction
    def autoconversion(self, item: AutoConversionItem) -> None:
        Wallet._autoconversion(item, self._assets)

    @staticmethod
    def _autoconversion(item: AutoConversionItem, assets: Dict[str, Decimal]) -> None:
        """autoconversion if effectively the same as exchange"""
        # check transaction possible
        if item.conversion_from.currency not in assets:
            raise InsufficientAssetError(f"Tried to autoconvert {item.conversion_from}, but no such asset in the wallet: {assets}, id: {item.transaction_id}")
        if item.conversion_from.amount > assets[item.conversion_from.currency]:
            raise InsufficientAssetError(
                f"Tried to autoconvert {item.conversion_from}, but only has {assets[item.conversion_from.currency]}, id: {item.transaction_id}"
            )

        # apply transaction
        assets[item.conversion_from.currency] -= item.conversion_from.amount
        assets[item.conversion_to.currency] += item.conversion_to.amount

    def dividend(self, item: DividendItem) -> None:
        self._assets[item.received_dividend.currency] += item.received_dividend.amount

        # first receive money, then autoconvert if needed. Eg. happens for Singapor dollars SGD -> USD
        for autoconversion in item.autoconversions:
            Wallet._autoconversion(autoconversion, self._assets)

        # issuance fee is always less than received dividend so no need to check for sufficient money
        if item.paid_issuance_fee is not None:
            self._assets[item.paid_issuance_fee.paid_fee.currency] -= item.paid_issuance_fee.paid_fee.amount

        # tax is always less than received dividend so no need to check for sufficient money
        if item.paid_tax is not None:
            self._assets[item.paid_tax.paid_tax.currency] -= item.paid_tax.paid_tax.amount

    def tax(self, item: TaxItem) -> None:
        # check transaction possible
        if item.paid_tax.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to pay tax {item.paid_tax}, but no such currency in the wallet")
        if item.paid_tax.amount > self._assets[item.paid_tax.currency]:
            raise InsufficientAssetError(f"Tried to pay tax {item.paid_tax}, but only has {self._assets[item.paid_tax.currency]}; item: {item}")

        # apply transaction
        self._assets[item.paid_tax.currency] -= item.paid_tax.amount

    def issuance_fee(self, item: IssuanceFeeItem) -> None:
        # check transaction possible
        if item.paid_fee.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to pay issuance fee {item.paid_fee}, but no such currency in the wallet")
        if item.paid_fee.amount > self._assets[item.paid_fee.currency]:
            raise InsufficientAssetError(f"Tried to pay issuance fee {item.paid_fee}, but only has {self._assets[item.paid_fee.currency]}")

        # apply transaction
        self._assets[item.paid_fee.currency] -= item.paid_fee.amount

    def corporate_action(self, item: CorporateActionItem) -> None:
        # check transaction possible
        if item.from_share.symbol not in self._assets:
            raise InsufficientAssetError(f"Tried to corporate action from {item.from_share}, but no such share in the wallet")
        if item.from_share.amount > self._assets[item.from_share.symbol]:
            raise InsufficientAssetError(f"Tried to corporate action from {item.from_share}, but only has {self._assets[item.from_share.symbol]}")

        # apply transaction
        self._assets[item.from_share.symbol] -= item.from_share.amount
        self._assets[item.to_share.symbol] += item.to_share.amount

    def fee(self, item: FeeItem) -> None:
        # check transaction possible
        if item.paid_fee.currency not in self._assets:
            raise InsufficientAssetError(f"Tried to pay fee {item.paid_fee}, but no such currency in the wallet")
        if item.paid_fee.amount > self._assets[item.paid_fee.currency]:
            raise InsufficientAssetError(f"Tried to pay fee {item.paid_fee}, but only has {self._assets[item.paid_fee.currency]}")

        # apply transaction
        self._assets[item.paid_fee.currency] -= item.paid_fee.amount

    def stock_split(self, item: StockSplitItem) -> None:
        # check transaction possible
        if item.from_share.symbol not in self._assets:
            raise InsufficientAssetError(f"Tried to stock split from {item.from_share}, but no such share in the wallet")
        if item.from_share.amount > self._assets[item.from_share.symbol]:
            raise InsufficientAssetError(f"Tried to stock split from {item.from_share}, but only has {self._assets[item.from_share.symbol]}")

        # apply transaction
        self._assets[item.from_share.symbol] -= item.from_share.amount
        self._assets[item.to_share.symbol] += item.to_share.amount

    def buy(self, item: BuyItem) -> None:
        # check transaction possible
        assets = self.assets_copy

        # 1. first autoconvert money if needed
        for autoconversion in item.autoconversions:
            Wallet._autoconversion(autoconversion, assets)

        # 2. then try paying for asset
        assets[item.paid.currency] -= item.paid.amount
        assets[item.commission.currency] -= item.commission.amount
        if assets[item.paid.currency] < 0 or assets[item.commission.currency] < 0:
            raise InsufficientAssetError(f"Tried to buy {item.__dict__} but insufficient money")

        # apply transaction
        for autoconversion in item.autoconversions:
            Wallet._autoconversion(autoconversion, self._assets)
        self._assets[item.asset_name] += item.amount
        self._assets[item.paid.currency] -= item.paid.amount
        self._assets[item.commission.currency] -= item.commission.amount

    def sell(self, item: SellItem) -> None:
        # check transaction possible

        # 1. First deduct asset and add money
        assets = self.assets_copy
        assets[item.asset_name] -= item.amount
        assets[item.received.currency] += item.received.amount

        # 2. Next do autoconversions, because exante first converts all received money, and then converts back just to pay commission. stupid
        for autoconversion in item.autoconversions:
            Wallet._autoconversion(autoconversion, assets)

        # 3. And then pay commission as we now have money for that
        assets[item.commission.currency] -= item.commission.amount
        if  assets[item.commission.currency] < 0:
            raise InsufficientAssetError(f"Tried to sell {item.__dict__} but insufficient money: {assets[item.commission.currency]}")

        if assets[item.asset_name] < 0 :
            raise InsufficientAssetError(f"Tried to sell {item.__dict__} but insufficient asset: {assets[item.commission.asset_name]}")


        # apply transaction
        self._assets[item.asset_name] -= item.amount
        self._assets[item.received.currency] += item.received.amount
        for autoconversion in item.autoconversions:
            Wallet._autoconversion(autoconversion, self._assets)
        self._assets[item.commission.currency] -= item.commission.amount

    @property
    def assets_copy(self) -> Dict[str, Decimal]:
        return copy.deepcopy(self._assets)
