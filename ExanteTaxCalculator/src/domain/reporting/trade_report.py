from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict

from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.tax_calculator import CalculationResult


@dataclass(frozen=True)
class TradeReport:
    dividends: List[DividendItemPLN]
    taxes: List[TaxItemPLN]
    profits: Dict[str, List[ProfitPLN]]
    results: CalculationResult
