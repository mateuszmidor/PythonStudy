""" 
In report, when the ID of subsequent rows increase it means the rows build a single transaction, eg. for dividend with tax:
1001 DIVIDEND  2001-12-20 15:10:45
1002 TAX       2001-12-20 15:10:45

When the ID drops, it means a new transaction begins, eg. for series of separate dividends:
1001 DIVIDEND  2001-12-20 15:10:45
501  DIVIDEND  2001-12-07 15:10:45
203  DIVIDEND  2001-12-02 15:10:45
"""

import csv
import datetime
from typing import List, Iterable, Sequence, Optional
from decimal import Decimal
from money import Money
from copy import deepcopy
from src.domain.transactions import *
from src.domain.currency import Currency
from src.infrastructure.report_row import ReportRow
from src.infrastructure.trade_item_builder import TradeItemBuilder
from src.infrastructure.errors import CorruptedReportError


class TradesRepoCSV:
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
    ]

    def __init__(self) -> None:
        self._last_transaction_id: int = -1
        self._builder = TradeItemBuilder()
        self._items: List[TransactionItem] = []

    def _is_beginning_of_new_item(self, row: ReportRow) -> bool:
        return self._last_transaction_id != -1 and row.transaction_id < self._last_transaction_id

    def _push_row(self, row: ReportRow) -> None:
        self._builder.add(row)
        self._last_transaction_id = row.transaction_id

    def _push_item(self) -> None:
        trade = self._builder.build()
        self._items.append(trade)

    def load(self, report_csv_lines: Sequence[str], delimiter: str = "\t") -> None:
        reader = csv.DictReader(f=report_csv_lines, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_ALL)

        # check csv header is present and formed as expected
        self._validate_header(reader.fieldnames)

        # check for empty report (just header)
        if len(report_csv_lines) == 1:
            return

        for row_dict in reader:
            row = ReportRow.from_dict(row_dict)
            if self._is_beginning_of_new_item(row):
                self._push_item()
            self._push_row(row)

        self._push_item()
        self._sort_items_by_date_ascending()

    @property
    def items(self) -> List[TransactionItem]:
        """ Items are sorted by date, ascending """

        return deepcopy(self._items)

    def _validate_header(self, header: Optional[Iterable[str]]) -> None:
        if header is None:
            raise CorruptedReportError("Missing header")

        expected = ",".join(TradesRepoCSV.EXPECTED_HEADER)
        actual = ",".join(header)

        if expected != actual:
            raise CorruptedReportError(f"Unexpected header format. Want: {expected}, got: {actual}")

    def _sort_items_by_date_ascending(self) -> None:
        # sort so that funding comes before withdrawal
        date = lambda item: item.date
        self._items.sort(key=date)