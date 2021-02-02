from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from src.domain.transactions import DividendItem


@dataclass(frozen=True)
class DividendItemPLN:
    source: DividendItem
    dividend_pln_quotation_date: datetime
    received_dividend_pln: Decimal
    tax_pln_quotation_date: datetime
    paid_tax_pln: Decimal

    def __post_init__(self) -> None:
        if self.dividend_pln_quotation_date >= self.source.date:
            raise ValueError(
                f"dividend_pln_quotation_date must be before dividend date, got: buy {self.dividend_pln_quotation_date}, sell {self.source.date}"
            )
