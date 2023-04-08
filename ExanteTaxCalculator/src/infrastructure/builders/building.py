from typing import Union, Optional, List
from money import Money

from src.domain.transactions import *
from src.domain.currency import Currency
from src.domain.share import Share

from src.infrastructure.report_row import ReportRow
from src.infrastructure.transaction_item_data import TransactionItemData
from src.infrastructure.errors import InvalidTradeError, InvalidReportRowError

from abc import ABC, abstractmethod
from src.infrastructure.report_row import ReportRow
from src.infrastructure.transaction_item_data import TransactionItemData


class Builder(ABC):
    """Builder takes a series of ReportRows and turns them into actual TransactionItem"""

    @abstractmethod
    def add(self, row: ReportRow) -> bool:
        pass

    @abstractmethod
    def build(self) -> TransactionItem:
        pass


# class NullBuilder(Builder):
#     def add(self, row: ReportRow) -> bool:
#         return False

#     def build(self) -> TransactionItem:
#         return


def is_money(row: Optional[ReportRow]) -> bool:
    return row is not None and Currency.is_currency(row.asset)


def build_autoconversions(items: List[TransactionItemData]) -> List[AutoConversionItem]:
    results: List[AutoConversionItem] = []
    for item in items:
        assert len(item.decrease) == 1, f"expected 1, was {len(item.decrease)}, items: {items}"
        assert item.increase is not None
        assert item.transaction_id is not None
        result = AutoConversionItem(
            conversion_from=-Money(item.decrease[0].sum, item.decrease[0].asset),
            conversion_to=Money(item.increase.sum, item.increase.asset),
            date=item.increase.when,
            transaction_id=item.transaction_id,
        )
        results.append(result)
    return results
