import datetime
from decimal import Decimal
from dataclasses import dataclass

from src.domain.taxable_item import TaxableItem


@dataclass
class TaxableItemPLNQuoted(TaxableItem):

    buy_pln_quotation_date: datetime.date
    buy_paid_pln: Decimal
    buy_commission_pln: Decimal

    sell_pln_quotation_date: datetime.date 
    sell_received_pln: Decimal 
    sell_commission_pln: Decimal

    def __post_init__(self) -> None:
        if self.buy_pln_quotation_date > self.sell_pln_quotation_date:
            raise ValueError(f"buy_pln_quotation_date must be before sell_pln_quotation_date, got: buy {self.buy_pln_quotation_date}, sell {self.sell_pln_quotation_date}")

    @classmethod
    def from_taxable_item(cls, item: TaxableItem, 
                            buy_pln_quotation_date: datetime.date, buy_paid_pln: Decimal, buy_commission_pln: Decimal,
                            sell_pln_quotation_date: datetime.date, sell_received_pln: Decimal, sell_commission_pln: Decimal):
        return cls(
            asset_name = item.asset_name,

            buy_amount = item.buy_amount,
            buy_paid = item.buy_paid,
            buy_commission = item.buy_commission,
            buy_date = item.buy_date,
            buy_transaction_id = item.buy_transaction_id,

            sell_amount = item.sell_amount,
            sell_received = item.sell_received,
            sell_commission = item.sell_commission, 
            sell_date = item.sell_date,
            sell_transaction_id = item.sell_transaction_id,

            buy_pln_quotation_date = buy_pln_quotation_date,
            buy_paid_pln = buy_paid_pln,
            buy_commission_pln = buy_commission_pln,
            sell_pln_quotation_date = sell_pln_quotation_date,
            sell_received_pln = sell_received_pln,
            sell_commission_pln = sell_commission_pln
        )