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


class AutoConversionBuilder(Builder):
    """
    AutoConversionBuilder turns ReportRows into standalone AutoConversionItem
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
        if row.operation_type not in {ReportRow.OperationType.AUTOCONVERSION}:
            return False

        # check if ready to build
        if len(self._item.autoconversions) == 1 and self._item.autoconversions[0].increase != None and len(self._item.autoconversions[0].decrease) == 1:
            return False

        return self._item.add_row(row)

    def build(self) -> TransactionItem:
        if len(self._item.autoconversions) == 1 and self._item.autoconversions[0].increase != None and len(self._item.autoconversions[0].decrease) == 1:
            return self._build_autoconversion_item()
        else:
            raise InvalidTradeError(f"Unrecognized autoconversion type:\nitem: {self._item}")

    def _build_autoconversion_item(self) -> AutoConversionItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for autoconversion: {commission}")
        inc = self._item.autoconversions[0].increase
        dec = self._item.autoconversions[0].decrease[0]  # len==1 checked during operation classification
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        return AutoConversionItem(
            conversion_from=-Money(dec.sum, dec.asset),
            conversion_to=Money(inc.sum, inc.asset),
            date=dec.when,
            transaction_id=transaction_id,
        )
