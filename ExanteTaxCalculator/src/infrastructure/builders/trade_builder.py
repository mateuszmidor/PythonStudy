from typing import Union, Optional, List
from money import Money

from decimal import Decimal
from src.domain.transactions import *
from src.domain.currency import Currency
from src.domain.share import Share

from src.infrastructure.report_row import ReportRow
from src.infrastructure.transaction_item_data import TransactionItemData
from src.infrastructure.errors import InvalidTradeError, InvalidReportRowError
from src.infrastructure.builders.building import build_autoconversions, is_money, Builder


class TradeBuilder(Builder):
    """
    TradeItemBuilder turns ReportRows int BuyItem/SellItem/ExchangeItem
    """

    def __init__(self) -> None:
        super().__init__()
        self._item = TransactionItemData()
        self._uuids : list[str] = []

    def add(self, row: ReportRow) -> bool:
        """Returns False if the row could not be added - meaning that the item is complete and ready to build"""

        # uuid is used to link autoconversion with trade; they occur in sequence: first trade with uuid, then autoconversions with parent_uuid = uuid
        self._uuids.append(row.uuid)

        # check if we are still processing the same transaction that we began with
        if row.parent_uuid not in self._uuids and not self.transaction_continues(row.symbol_id) :
            print("### new transaction ended")
            return False

        # check if the operation is applicable for this item type
        if row.operation_type not in {ReportRow.OperationType.TRADE, ReportRow.OperationType.COMMISSION, ReportRow.OperationType.AUTOCONVERSION}:
            print("### invalid transaction type")
            return False

        # specific to TradeItem: there can be only 1 decrease action
        if row.sum < 0 and row.operation_type == ReportRow.OperationType.TRADE and len(self._item.decrease) == 1:
            print("### decrease found")
            return False

        # specific to TradeItem: money exchange cant have AUTOCONVERSION actions
        if (
            row.operation_type == ReportRow.OperationType.AUTOCONVERSION
            and is_money(self._item.increase)
            and len(self._item.decrease) > 0
            and is_money(self._item.decrease[0])
        ):
            print("### autoconversion")
            return False

        return self._item.add_row(row)

    def build(self) -> TransactionItem:
        inc = self._item.increase
        dec = self._item.decrease

        # increase money and decrease money -> money exchange
        if is_money(inc) and len(dec) == 1 and is_money(dec[0]):
            return self._build_exchange_item()
        # increase shares and decrease money -> buy
        elif not is_money(inc) and len(dec) == 1 and is_money(dec[0]):
            return self._build_buy_item()
        # increase money and decrease asset -> sell
        elif is_money(inc) and len(dec) == 1 and not is_money(dec[0]):
            return self._build_sell_item()
        else:
            raise InvalidTradeError(f"Unrecognized trade type, not buy/sell/money-exchange:\ninc: {inc}\ndec: {dec}")

    def _build_exchange_item(self) -> ExchangeItem:
        """Money exchange is stored under TRADE item"""
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for money exchange: {commission}")
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        return ExchangeItem(
            exchange_from=-Money(dec.sum, dec.asset),
            exchange_to=Money(inc.sum, inc.asset),
            date=dec.when,
            transaction_id=transaction_id,
        )

    def _build_buy_item(self) -> BuyItem:
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        commission = self._item.commission
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        paid = -Money(dec.sum, dec.asset)
        commision = Money("0", dec.asset) if commission is None else -Money(commission.sum, commission.asset)
        autoconversions = build_autoconversions(self._item.autoconversions)

        return BuyItem(
            asset_name=inc.asset,
            amount=inc.sum,
            paid=paid,
            commission=commision,
            date=inc.when,
            transaction_id=transaction_id,
            autoconversions=autoconversions,
        )

    def _build_sell_item(self) -> SellItem:
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        commission = self._item.commission
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        received = Money(inc.sum, inc.asset)
        commission = Money("0", inc.asset) if commission is None else -Money(commission.sum, commission.asset)
        autoconversions = build_autoconversions(self._item.autoconversions)

        return SellItem(
            asset_name=dec.asset,
            amount=-dec.sum,
            received=received,
            commission=commission,
            autoconversions=autoconversions,
            date=dec.when,
            transaction_id=transaction_id,
        )
