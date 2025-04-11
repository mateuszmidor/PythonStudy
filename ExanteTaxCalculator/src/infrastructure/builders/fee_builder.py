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


class FeeBuilder(Builder):
    """
    FeeBuilder turns ReportRows into FeeItem
    """

    def __init__(self) -> None:
        super().__init__()
        self._item = TransactionItemData()

    def add(self, row: ReportRow) -> bool:
        """Returns False if the row could not be added - meaning that the item is complete and ready to build"""

        # check if we are still processing the same transaction that we began with
        if not self.transaction_continues(row.symbol_id):
            return False

        # check if the operation is applicable for this item type
        if row.operation_type not in {ReportRow.OperationType.FEE}:
            return False

        if len(self._item.decrease) == 1:
            return False

        return self._item.add_row(row)

    def build(self) -> TransactionItem:
        inc = self._item.increase
        dec = self._item.decrease

        # decrease money -> fee
        if inc == None and len(dec) == 1 and is_money(dec[0]):
            return self._fee_item()
        else:
            raise InvalidTradeError(f"Unrecognized fee type:\ninc: {inc}\ndec: {dec}")

    def _fee_item(self) -> FeeItem:
        dec = self._item.decrease[0]
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return FeeItem(paid_fee=-Money(dec.sum, dec.asset), date=dec.when, transaction_id=transaction_id, comment=dec.comment)
