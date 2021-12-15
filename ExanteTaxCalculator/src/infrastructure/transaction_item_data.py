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

    def add_row(self, row: ReportRow) -> None:
        # first row making an item provides transaction_id
        if self.transaction_id is None:
            self.transaction_id = row.transaction_id

        if row.operation_type == ReportRow.OperationType.COMMISSION:
            self._push_commission(row)
        elif row.operation_type == ReportRow.OperationType.AUTOCONVERSION:
            self._push_autoconversion(row)
        elif row.sum > 0:
            self.increase = row
        elif row.sum < 0:
            self.decrease.append(row)
        else:
            raise InvalidReportRowError(f"Invalid report row: {row}")

    def _push_autoconversion(self, row: ReportRow) -> None:
        if len(self.autoconversions) == 0 or (self.autoconversions[-1].increase != None and self.autoconversions[-1].decrease != []):
            self.autoconversions.append(TransactionItemData())
            self.autoconversions[-1].transaction_id = row.transaction_id

        if row.sum > 0:
            self.autoconversions[-1].increase = row
        else:
            self.autoconversions[-1].decrease.append(row)

    def _push_commission(self, row: ReportRow) -> None:
        if not is_money(row):
            raise InvalidReportRowError(f"Commission should be money, got: {row}")
        if row.sum >= 0:
            raise InvalidReportRowError(f"Commission should be negative (substracted from account), got: {row}")

        self.commission = row
