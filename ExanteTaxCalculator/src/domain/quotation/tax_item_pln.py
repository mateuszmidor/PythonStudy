from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from src.domain.transactions import TaxItem


@dataclass(frozen=True)
class TaxItemPLN:
    source: TaxItem
    tax_pln_quotation_date: datetime
    paid_tax_pln: Decimal

    def __post_init__(self) -> None:
        if self.tax_pln_quotation_date >= self.source.date:
            raise ValueError(f"tax_pln_quotation_date must be before tax date, got: buy {self.tax_pln_quotation_date}, sell {self.source.date}")
