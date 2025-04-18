from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Dict

from src.infrastructure.errors import InvalidReportRowError


@dataclass
class ReportRow:
    """ReportRow is raw CSV report row parsed into a dataclass."""

    class OperationType(Enum):
        """Names reflect Exante Transaction Report 'Operation type' column"""

        UNKNOWN = "UNKNOWN"
        TRADE = "TRADE"
        COMMISSION = "COMMISSION"
        FUNDING_WITHDRAWAL = "FUNDING/WITHDRAWAL"
        AUTOCONVERSION = "AUTOCONVERSION"
        DIVIDEND = "DIVIDEND"
        TAX = "TAX"
        US_TAX = "US TAX"
        CORPORATE_ACTION = "CORPORATE ACTION"
        ISSUANCE_FEE = "ISSUANCE FEE"
        STOCK_SPLIT = "STOCK SPLIT"
        FEE = "FEE"

    transaction_id: int
    account_id: str
    symbol_id: str
    operation_type: OperationType
    when: datetime
    sum: Decimal
    asset: str
    eur_equivalent: Decimal
    comment: str
    uuid: str = "" # here and parent_uuid have defalt "" to satisfy hordes of unit tests
    parent_uuid: str = "" # in case of autoconversion resulting from trade, here is the "uuid" of the trade causing autoconversion

    def __post_init__(self):
        if self.transaction_id < 0:
            raise InvalidReportRowError(f"transaction_id should be >= 0, got: {self.transaction_id}")

        if self.account_id == "":
            raise InvalidReportRowError("account_id should not be empty")

        if self.symbol_id == "":
            raise InvalidReportRowError("symbol_id should not be empty")

        if self.asset == "":
            raise InvalidReportRowError("asset should not be empty")

        # actually, sum can be 0 for COMMISSION
        # if self.sum == 0:
        # raise InvalidReportRowError("sum should not be zero")

    @classmethod
    def from_dict(cls, d: Dict[str, str]):
        try:
            return cls(
                transaction_id=int(d["Transaction ID"]),
                account_id=d["Account ID"],
                symbol_id=d["Symbol ID"],
                operation_type=ReportRow.OperationType(d["Operation type"]),
                when=datetime.strptime(d["When"], "%Y-%m-%d %H:%M:%S"),
                sum=Decimal(d["Sum"]),
                asset=d["Asset"],
                eur_equivalent=Decimal(d["EUR equivalent"]),
                comment=d["Comment"],
                uuid=d.get("UUID", ""),
                parent_uuid=d.get("Parent UUID", "")
            )
        except (KeyError, ValueError) as e:
            raise InvalidReportRowError from e

    def __str__(self) -> str:
        lines = [f"{field.name} = {getattr(self, field.name)}" for field in fields(self)]
        return "\n".join(lines)
