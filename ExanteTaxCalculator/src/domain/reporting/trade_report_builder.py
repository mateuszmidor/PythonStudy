from typing import List
from datetime import date

from src.domain.reporting.report_item import ReportItem
from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN


class TradeReportBuilder:
    @staticmethod
    def build(profits: List[ProfitPLN], dividends: List[DividendItemPLN], taxes: List[TaxItemPLN]) -> List[ReportItem]:
        """
        Returned items are sorted by accounting date, ascending.
        Accounting date means:
        - for ProfitItem - date of sell
        - for DividendItem - date of dividend pay out
        - for TaxItem - date when the tax was deducted
        """

        items = list(profits)
        items.extend(dividends)
        items.extend(taxes)
        items.sort(key=get_item_accounting_date)

        return items


def get_item_accounting_date(item: ReportItem) -> date:
    """ Get date when the item is put into accounting book; when it generates tax obligation """

    if isinstance(item, ProfitPLN):
        return item.source.source.sell.date
    elif isinstance(item, DividendItemPLN):
        return item.source.date
    elif isinstance(item, TaxItemPLN):
        return item.source.date
    else:
        raise ValueError(f"Expected ReportItem, got: {item}")
