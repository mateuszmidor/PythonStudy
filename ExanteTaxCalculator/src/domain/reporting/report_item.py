from typing import Union

from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN


ReportItem = Union[ProfitPLN, DividendItemPLN, TaxItemPLN]
""" ReportItem is item that entails obligation of paying tax """
