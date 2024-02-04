"""
In a report, the rows may come not exactly sorted by TransactionID in ascending order.
Such ordering is required to correctly build TransactionItems from ReportRows.
Repo will ensure such ordering.
"""

import csv
from typing import List, Iterable, Sequence, Optional, Set
from copy import deepcopy
from src.domain.transactions import *
from src.infrastructure.report_row import ReportRow
from src.infrastructure.trade_item_builder import TradeItemBuilder
from src.infrastructure.errors import CorruptedReportError
from src.infrastructure.errors import InvalidTradeError
from src.infrastructure.builders.building import Builder
from src.infrastructure.builders import (
    TradeBuilder,
    FoundingWithdrawalBuilder,
    TaxBuilder,
    IssuanceFeeBuilder,
    CorporateActionBuilder,
    StockSplitBuilder,
    DividendBuilder,
    AutoConversionBuilder,
    SentinelBuilder,
)


class TradesRepoCSV2:
    """
    TradesRepoCSV reads repo CSV file row by row and matches multi-row items into actual TransactionItems.
    EG. for BuyItem there are 3 rows:
    - money paid
    - asset received
    - commission paid
    """

    EXPECTED_HEADER = [
        "Transaction ID",
        "Account ID",
        "Symbol ID",
        "Operation type",
        "When",
        "Sum",
        "Asset",
        "EUR equivalent",
        "Comment",
        "UUID",
        "Parent UUID"
    ]

    def __init__(self) -> None:
        self._items: List[TransactionItem] = []

    def load(self, report_csv_lines: Sequence[str], delimiter: str = "\t") -> None:
        # parse Exante report CSV lines into ReportRows
        report_rows = self._csv_to_report_rows(report_csv_lines, delimiter)

        # filter rollbacks
        filtered_rows = filter_rollbacked_rows(report_rows)

        # ReportRows need to be processed in ascending transaction_id order
        sorted_rows = sort_rows_by_transactionid_ascendig(filtered_rows)

        # stop processing if no rows to be processed
        if len(sorted_rows) == 0:
            return

        # build TransactionItems from ReportRows
        builder: Builder = SentinelBuilder()
        for rown, row in enumerate(sorted_rows):
            print(f"Processing row {rown}, transaction: {row.transaction_id}")

            if isinstance(builder, SentinelBuilder):
                print(f"NEW BUILDER: {row.operation_type}")
                builder = self._get_builder(row.operation_type)

            if not builder.add(row):
                self._items.append(builder.build())
                print(f"NEW BUILDER: {row.operation_type}")
                builder = self._get_builder(row.operation_type)
                builder.add(row)
            print(row)
            print()
        # append the final TransactionItems
        self._items.append(builder.build())

    @property
    def items(self) -> List[TransactionItem]:
        """Items are sorted by date, ascending"""

        return deepcopy(self._items)

    def _get_builder(self, op: ReportRow.OperationType) -> Builder:
        if op == ReportRow.OperationType.TRADE:
            return TradeBuilder()
        elif op == ReportRow.OperationType.FUNDING_WITHDRAWAL:
            return FoundingWithdrawalBuilder()
        elif op == ReportRow.OperationType.TAX:
            return TaxBuilder()
        elif op == ReportRow.OperationType.US_TAX:
            return TaxBuilder()
        elif op == ReportRow.OperationType.ISSUANCE_FEE:
            return IssuanceFeeBuilder()
        elif op == ReportRow.OperationType.CORPORATE_ACTION:
            return CorporateActionBuilder()
        elif op == ReportRow.OperationType.STOCK_SPLIT:
            return StockSplitBuilder()
        elif op == ReportRow.OperationType.DIVIDEND:
            return DividendBuilder()
        elif op == ReportRow.OperationType.AUTOCONVERSION:
            return AutoConversionBuilder()
        else:
            raise InvalidTradeError(f"Unknown trading operation: {op}")

    def _validate_header(self, header: Optional[Iterable[str]]) -> None:
        if header is None:
            raise CorruptedReportError("Missing header")

        missing_columns = [c for c in TradesRepoCSV2.EXPECTED_HEADER if c not in header]

        if len(missing_columns) > 0:
            raise CorruptedReportError(f"Missing columns in header: {missing_columns}")

    def _csv_to_report_rows(self, report_csv_lines: Sequence[str], delimiter: str) -> List[ReportRow]:
        reader = csv.DictReader(f=report_csv_lines, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_ALL)

        # check csv header is present and formed as expected
        self._validate_header(reader.fieldnames)

        # parse the lines into ReportRow items
        return [ReportRow.from_dict(d) for d in reader]


def filter_rollbacked_rows(rows: List[ReportRow]) -> List[ReportRow]:
    """Need to filter both, rolled back rows and rows specifying the rollbacks"""
    import re

    TRANSACTION_ID_PATTERN = r"#\d+"  # e.g. "#123456"

    transactions_to_remove: Set[int] = set()

    for row in rows:
        findings = re.findall(TRANSACTION_ID_PATTERN, row.comment)
        if len(findings) == 1:
            found_hash_id = findings[0]
            transaction_id_to_rollback = int(found_hash_id[1:])  # skip the prefix '#' in #123456
            transactions_to_remove.add(transaction_id_to_rollback)  # remove transaction to rollback
            transactions_to_remove.add(row.transaction_id)  # remove the rollbacker itself
        elif len(findings) > 1:
            print(f"More than one transaction to rollback? - {row.comment}, {findings}")

    return [row for row in rows if row.transaction_id not in transactions_to_remove]


def sort_rows_by_transactionid_ascendig(rows: List[ReportRow]) -> List[ReportRow]:
    sort_by_transaction_id = lambda row: row.transaction_id
    rows.sort(key=sort_by_transaction_id)
    return rows
