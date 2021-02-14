from typing import List, Dict
from collections import defaultdict
from money import Money
from decimal import Decimal

from src.domain.reporting.trade_report import TradeReport
from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.tax_calculator import CalculationResult
from src.domain.transactions import TaxItem


class TradeReportBuilder:
    @staticmethod
    def build(profits: List[ProfitPLN], dividends: List[DividendItemPLN], taxes: List[TaxItemPLN], results: CalculationResult) -> TradeReport:
        return TradeReport(
            dividends=dividends,
            taxes=TradeReportBuilder._concat_taxes(taxes, dividends),
            profits=TradeReportBuilder._group_profits_by_asset(profits),
            results=results,
        )

    @staticmethod
    def _concat_taxes(taxes: List[TaxItemPLN], dividends: List[DividendItemPLN]) -> List[TaxItemPLN]:
        result = taxes
        for d in dividends:
            if d.paid_tax_pln == Decimal(0):
                continue

            source = TaxItem(paid_tax=d.source.paid_tax, date=d.source.date)  # dummy source; will be removed when DividendItem contains full TaxItem
            tax = TaxItemPLN(source=source, tax_pln_quotation_date=d.tax_pln_quotation_date, paid_tax_pln=d.paid_tax_pln)
            result.append(tax)
        return result

    @staticmethod
    def _group_profits_by_asset(profits: List[ProfitPLN]) -> Dict[str, List[ProfitPLN]]:
        result: Dict[str, List[ProfitPLN]] = defaultdict(list)
        for p in profits:
            name = p.source.source.sell.asset_name
            group = result[name]
            group.append(p)
        return result
