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


class FoundingWithdrawalBuilder(Builder):
    """
    FoundingWithdrawalBuilder turns ReportRows into FoundingItem/WithdrawalItem
    """

    def __init__(self) -> None:
        super().__init__()
        self._item = TransactionItemData()

    def add(self, row: ReportRow) -> bool:
        """Returns False if the row could not be added - meaning that the item is complete and ready to build"""

        # check if the operation is applicable for this item type
        if row.operation_type not in {ReportRow.OperationType.FUNDING_WITHDRAWAL}:
            return False

        # specific to TradeItem: there can be only 1 increase or decrease action
        if self._item.increase != None or self._item.decrease != []:
            return False

        return self._item.add_row(row)

    def build(self) -> TransactionItem:
        inc = self._item.increase
        dec = self._item.decrease

        # increase money -> founding
        if is_money(inc) and dec == []:
            return self._build_funding_item()
        # decrease money -> withdrawal
        elif inc == None and len(dec) == 1 and is_money(dec[0]):
            return self._build_withdrawal_item()
        else:
            raise InvalidTradeError(f"Unrecognized founding/withdrawal type, not founding/withdrawal:\ninc: {inc}\ndec: {dec}")

    def _build_funding_item(self) -> FundingItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for funding: {commission}")
        inc = self._item.increase
        assert inc is not None
        if not is_money(inc):
            raise InvalidTradeError(f"Tried funding with non-money: {inc}")
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return FundingItem(funding_amount=Money(inc.sum, inc.asset), date=inc.when, transaction_id=transaction_id)

    def _build_withdrawal_item(self) -> WithdrawalItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for withdrawal: {commission}")
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        if not is_money(dec):
            raise InvalidTradeError(f"Tried withdrawal with non-money: {dec}")
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return WithdrawalItem(-Money(dec.sum, dec.asset), dec.when, transaction_id)
