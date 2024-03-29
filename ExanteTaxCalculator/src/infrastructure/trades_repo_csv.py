""" 
In report, when the ID of subsequent rows increase it means the rows build a single transaction, eg. for dividend with tax:
1001 DIVIDEND  2001-12-20 15:10:45
1002 TAX       2001-12-20 15:10:45

When the ID drops, it means a new transaction begins, eg. for series of separate dividends:
1001 DIVIDEND  2001-12-20 15:10:45
501  DIVIDEND  2001-12-07 15:10:45
203  DIVIDEND  2001-12-02 15:10:45

After parsing all rows, the items are sorted ascending 1. by date 2. by transaction id, so funding is first item
"""

import csv
from typing import List, Iterable, Sequence, Optional
from copy import deepcopy
from src.domain.transactions import *
from src.infrastructure.report_row import ReportRow
from src.infrastructure.trade_item_builder import TradeItemBuilder
from src.infrastructure.errors import CorruptedReportError
from src.infrastructure.errors import InvalidTradeError


class TradesRepoCSV:
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
    ]

    def __init__(self) -> None:
        self._last_transaction_id: int = -1
        self._last_symbol_id: str = ""
        self._builder = TradeItemBuilder()
        self._items: List[TransactionItem] = []

    def _is_beginning_of_new_item(self, row: ReportRow) -> bool:
        return self._last_transaction_id != -1 and row.transaction_id < self._last_transaction_id
        # return self._last_symbol_id != "" and row.symbol_id != self._last_symbol_id

    def _push_row(self, row: ReportRow) -> None:
        self._builder.add(row)
        self._last_transaction_id = row.transaction_id
        self._last_symbol_id = row.symbol_id

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

        n_row = 2  # row 1 is the header
        for row_dict in reader:
            row = ReportRow.from_dict(row_dict)
            print(f"processing row: {n_row}\n\t{row}")
            if self._is_beginning_of_new_item(row):
                try:
                    self._push_item()
                except InvalidTradeError as err:
                    raise InvalidTradeError(f"Row no (assuming headers is row 1 and no blank rows): {n_row}") from err

            self._push_row(row)
            n_row = n_row + 1

        self._push_item()
        self._sort_items_by_date_transactionid_ascending()

    @property
    def items(self) -> List[TransactionItem]:
        """Items are sorted by date, ascending"""

        return deepcopy(self._items)

    def _validate_header(self, header: Optional[Iterable[str]]) -> None:
        if header is None:
            raise CorruptedReportError("Missing header")

        missing_columns = [c for c in TradesRepoCSV.EXPECTED_HEADER if c not in header]

        if len(missing_columns) > 0:
            raise CorruptedReportError(f"Missing columns in header: {missing_columns}")

    def _sort_items_by_date_transactionid_ascending(self) -> None:
        # sort items by date so that funding comes before withdrawal,
        # sort also by transaction_id - in case transactions have same date we want to preserve actual order of events
        sorting_key = lambda item: (item.date, item.transaction_id)
        self._items.sort(key=sorting_key)
