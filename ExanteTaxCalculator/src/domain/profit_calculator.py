from money import Money
from decimal import Decimal
from dataclasses import dataclass
from src.domain.taxable_item_pln_quoted import TaxableItemPLNQuoted
from src.domain.profit_item import ProfitItem


class ProfitCalculator:
    def calc_profit(self, taxable: TaxableItemPLNQuoted) -> ProfitItem:
        profit = (
            taxable.sell_received_pln
            - taxable.sell_commission_pln
            - (taxable.buy_paid_pln + taxable.buy_commission_pln) * taxable.sell_amount / taxable.buy_amount
        )
        return ProfitItem(profit, taxable)
