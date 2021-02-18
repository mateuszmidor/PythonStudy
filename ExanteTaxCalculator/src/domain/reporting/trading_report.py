from dataclasses import dataclass
from typing import List, Dict

from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.tax_declaration.tax_declaration_numbers import TaxDeclarationNumbers


@dataclass(frozen=True)
class TradingReport:
    dividends: List[DividendItemPLN]
    taxes: List[TaxItemPLN]
    trades_by_asset: Dict[str, List[ProfitPLN]]
    results: TaxDeclarationNumbers
