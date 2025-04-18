from typing import List, Dict
from collections import defaultdict
from money import Money
from decimal import Decimal

from src.domain.reporting.trading_report import TradingReport
from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.tax_declaration.tax_declaration_numbers import TaxDeclarationNumbers
from src.domain.transactions import TaxItem


class TradingReportBuilder:
    @staticmethod
    def build(profits: List[ProfitPLN], dividends: List[DividendItemPLN], dividend_taxes: List[TaxItemPLN], results: TaxDeclarationNumbers) -> TradingReport:
        """ Note: taxes from dividends should be included on "taxes" list """

        return TradingReport(
            dividends=dividends,
            dividend_taxes=dividend_taxes,
            trades_by_asset=TradingReportBuilder._group_profits_by_asset(profits),
            results=results,
        )

    @staticmethod
    def _group_profits_by_asset(profits: List[ProfitPLN]) -> Dict[str, List[ProfitPLN]]:
        result: Dict[str, List[ProfitPLN]] = defaultdict(list)
        for p in profits:
            name = p.source.source.sell.asset_name
            group = result[name]
            group.append(p)

        return result
