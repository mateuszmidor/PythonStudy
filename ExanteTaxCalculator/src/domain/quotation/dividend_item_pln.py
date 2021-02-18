from datetime import date
from decimal import Decimal
from dataclasses import dataclass
from typing import Optional
from src.domain.transactions import DividendItem
from src.domain.quotation.tax_item_pln import TaxItemPLN


@dataclass(frozen=True)
class DividendItemPLN:
    source: DividendItem
    dividend_pln_quotation_date: date
    received_dividend_pln: Decimal
    paid_tax_pln: Optional[TaxItemPLN]

    def __post_init__(self) -> None:
        payout_date = self.source.date.date()
        if self.dividend_pln_quotation_date >= payout_date:
            raise ValueError(
                f"dividend_pln_quotation_date must be before dividend date, got: buy {self.dividend_pln_quotation_date}, sell {payout_date}"
            )
