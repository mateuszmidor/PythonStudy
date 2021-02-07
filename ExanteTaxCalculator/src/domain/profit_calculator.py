from money import Money
from decimal import Decimal
from dataclasses import dataclass
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.profit_item import ProfitItem


class ProfitCalculator:
    def calc_profit(self, taxable: BuySellPairPLN) -> ProfitItem:
        amount_sold = taxable.source.amount_sold
        # amount_sold = min(taxable.buy.amount, taxable.sell.amount) # this is faulty calcultion for testing purpose

        # the commission already increases the cost
        paid = (taxable.buy_paid_pln + taxable.buy_commission_pln) * amount_sold / taxable.source.buy.amount

        # the commission already decreases the income
        received = (taxable.sell_received_pln - taxable.sell_commission_pln) * amount_sold / taxable.source.sell.amount
        return ProfitItem(source=taxable, paid=paid, received=received)
