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


class StockSplitBuilder(Builder):
    """
    StockSplitBuilder turns ReportRows into StockSplitItem
    """

    def __init__(self) -> None:
        self._item = TransactionItemData()

    def add(self, row: ReportRow) -> bool:
        """Returns False if the row could not be added - meaning that the item is complete and ready to build"""

        # check if the operation is applicable for this item type
        if row.operation_type not in {ReportRow.OperationType.STOCK_SPLIT}:
            return False

        # ready to build
        if self._item.increase != None and len(self._item.decrease) == 1:
            return False

        return self._item.add_row(row)

    def build(self) -> TransactionItem:
        inc = self._item.increase
        dec = self._item.decrease

        if inc != None and len(self._item.decrease) == 1:
            return self._build_stock_split_item()
        else:
            raise InvalidTradeError(f"Unrecognized stock split type:\ninc: {inc}\ndec: {dec}")

    def _build_stock_split_item(self) -> StockSplitItem:
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification

        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None

        from_share = Share(amount=-dec.sum, symbol=dec.asset)
        to_share = Share(amount=inc.sum, symbol=inc.asset)
        return StockSplitItem(from_share=from_share, to_share=to_share, date=dec.when, transaction_id=transaction_id)
