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


class DividendBuilder(Builder):
    """
    DividendBuilder turns ReportRows into DividendItem
    """

    def __init__(self) -> None:
        self._item = TransactionItemData()

    def add(self, row: ReportRow) -> bool:
        """Returns False if the row could not be added - meaning that the item is complete and ready to build"""

        # check if the operation is applicable for this item type
        if row.operation_type not in {
            ReportRow.OperationType.DIVIDEND,
            ReportRow.OperationType.AUTOCONVERSION,
            ReportRow.OperationType.TAX,
            ReportRow.OperationType.ISSUANCE_FEE,
        }:
            return False

        # specific to DividendItem: there can be only 1 decrease action
        if row.sum < 0 and row.operation_type == ReportRow.OperationType.DIVIDEND and len(self._item.decrease) == 1:
            return False

        return self._item.add_row(row)

    def build(self) -> TransactionItem:
        inc = self._item.increase
        dec = self._item.decrease

        return self._build_dividend_item()
        # else:
        #     raise InvalidTradeError(f"Unrecognized dividend type:\ninc: {inc}\ndec: {dec}")

    def _build_dividend_item(self) -> DividendItem:
        """Dividend has required dividend part and optional tax part"""
        inc = self._item.increase
        assert inc is not None
        dec = self._item.decrease
        transaction_id = self._item.transaction_id
        autoconversions = build_autoconversions(self._item.autoconversions)
        assert inc is not None
        assert transaction_id is not None
        # tax may be none; not reported together with dividend
        # issuance fee may be none; not reported together with dividend
        # there can be both: tax and issuance fee. Face that...

        if len(dec) > 2:
            raise InvalidTradeError(f"Dividend can have at most 2 money stealers (Tax, Issuance Fee), but got: {dec}")

        tax = issuance_fee = None
        for dec_item in dec:
            if dec_item.operation_type == ReportRow.OperationType.TAX:
                tax = self._build_tax_item(dec_item)
            elif dec_item.operation_type == ReportRow.OperationType.ISSUANCE_FEE:
                issuance_fee = self._build_issuance_fee_item(dec_item)
            else:
                raise InvalidTradeError(f"Dividend allowed money stealers are (Tax, Issuance Fee), but got: {dec_item}")

        dividend = Money(inc.sum, inc.asset)
        return DividendItem(
            received_dividend=dividend,
            paid_tax=tax,
            paid_issuance_fee=issuance_fee,
            autoconversions=autoconversions,
            date=inc.when,
            transaction_id=transaction_id,
            comment=inc.comment,
        )

    def _build_tax_item(self, dec: ReportRow) -> TaxItem:
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return TaxItem(paid_tax=-Money(dec.sum, dec.asset), date=dec.when, transaction_id=transaction_id, comment=dec.comment)

    def _build_issuance_fee_item(self, dec: ReportRow) -> IssuanceFeeItem:
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return IssuanceFeeItem(paid_fee=-Money(dec.sum, dec.asset), date=dec.when, transaction_id=transaction_id, comment=dec.comment)
