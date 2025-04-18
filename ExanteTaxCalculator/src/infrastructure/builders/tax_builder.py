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


class TaxBuilder(Builder):
    """
    TaxBuilder turns ReportRows into TaxItem
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
        if row.operation_type not in {ReportRow.OperationType.TAX, ReportRow.OperationType.US_TAX}:
            return False

        if len(self._item.decrease) == 1:
            return False

        return self._item.add_row(row)

    def build(self) -> TransactionItem:
        inc = self._item.increase
        dec = self._item.decrease

        # decrease money -> tax deduction
        if inc == None and len(dec) == 1 and is_money(dec[0]):
            return self._build_tax_item()
        # increase money -> tax recalculation/return, eg. "Tax recalculation for 6.0 shares ExD 2024-09-05 PD 2024-09-19 dividend MOS.NYSE 1.26 USD (0.21 per share) tax -0.38 USD (-30.00%) DivCntry US"
        elif len(dec) == 0 and inc is not None and is_money(inc):
            return self._build_tax_item_recalc()
        else:
            raise InvalidTradeError(f"Unrecognized tax type:\ninc: {inc}\ndec: {dec}")

    def _build_tax_item(self) -> TaxItem:
        dec = self._item.decrease[0]

        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return TaxItem(paid_tax=-Money(dec.sum, dec.asset), date=dec.when, transaction_id=transaction_id, comment=dec.comment)

    def _build_tax_item_recalc(self) -> TaxItem:
        inc  = self._item.increase
        assert inc is not None

        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return TaxItem(paid_tax=-Money(inc.sum, inc.asset), date=inc.when, transaction_id=transaction_id, comment=inc.comment)