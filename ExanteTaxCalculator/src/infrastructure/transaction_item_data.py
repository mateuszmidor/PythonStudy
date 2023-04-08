from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass, field

from src.infrastructure.report_row import ReportRow
from src.infrastructure.errors import InvalidReportRowError
from src.domain.currency import Currency


def is_money(row: ReportRow) -> bool:
    return Currency.is_currency(row.asset)


@dataclass
class TransactionItemData:
    """
    TransactionItemData fills TransactionItem attributes from passed ReportRow.
    It helps in building TransactionItems from report CSV rows.
    """

    increase: Optional[ReportRow] = None  # single source of money increase eg. Sell received, Dividend received, Funding received
    decrease: List[ReportRow] = field(default_factory=list)  #  eg. in Dividend there can be both Tax and Issuance Fee
    commission: Optional[ReportRow] = None
    transaction_id: Optional[int] = None
    autoconversions: List[TransactionItemData] = field(default_factory=list)

    def reset(self) -> None:
        self.increase = self.commission = self.transaction_id = None
        self.decrease = []
        self.autoconversions = []

    def add_row(self, row: ReportRow) -> bool:
        # first row making an item provides transaction_id
        if self.transaction_id is None:
            self.transaction_id = row.transaction_id

        if row.operation_type == ReportRow.OperationType.COMMISSION:
            return self._push_commission(row)
        elif row.operation_type == ReportRow.OperationType.AUTOCONVERSION:
            return self._push_autoconversion(row)
        elif row.sum > 0:
            # check if increase already set
            if self.increase != None:
                return False
            self.increase = row
        elif row.sum < 0:
            self.decrease.append(row)
        else:
            raise InvalidReportRowError(f"Invalid report row: {row}")

        return True

    def _push_autoconversion(self, row: ReportRow) -> bool:
        last_item_complete = len(self.autoconversions) > 0 and self.autoconversions[-1].increase != None and self.autoconversions[-1].decrease != []

        # there should be at most 2 autoconversions
        if len(self.autoconversions) == 2 and last_item_complete:
            return False  # limit reached

        if len(self.autoconversions) == 0 or last_item_complete:
            self.autoconversions.append(TransactionItemData())
            self.autoconversions[-1].transaction_id = row.transaction_id

        if row.sum > 0:
            self.autoconversions[-1].increase = row
        else:
            self.autoconversions[-1].decrease.append(row)

        return True

    def _push_commission(self, row: ReportRow) -> bool:
        if not is_money(row):
            raise InvalidReportRowError(f"Commission should be money, got: {row}")
        if row.sum >= 0:
            raise InvalidReportRowError(f"Commission should be negative (substracted from account), got: {row}")

        # check if commission is already set
        if self.commission != None:
            return False

        self.commission = row
        return True
