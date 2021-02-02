from money import Money
from datetime import date, timedelta

from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.profit_item import ProfitPLN
from src.domain.transactions import *
from src.domain.reporting.trade_report_printer import TradeReportPrinter


def newProfit(when: date, profit_pln: int = 0) -> ProfitPLN:
    buy = BuyItem(asset_name="PHYS", amount=10, paid=Money(1000, "USD"), commission=Money(1, "USD"), date=date(2020, 1, 2))
    sell = SellItem(asset_name="PHYS", amount=10, received=Money(1000, "USD"), commission=Money(1, "USD"), date=when)
    buy_sell = BuySellPair(buy=buy, sell=sell, amount_sold=10)
    buy_sell_pln = BuySellPairPLN(
        source=buy_sell,
        buy_pln_quotation_date=date(2020, 1, 1),
        buy_paid_pln=3000,
        buy_commission_pln=3,
        sell_pln_quotation_date=when - timedelta(days=1),
        sell_received_pln=3000,
        sell_commission_pln=3,
    )
    return ProfitPLN(profit=profit_pln, source=buy_sell_pln)


def newTax(when: date, paid_pln: int = 0) -> TaxItemPLN:
    tax = TaxItem(paid_tax=Money(100, "USD"), date=when)
    return TaxItemPLN(source=tax, tax_pln_quotation_date=when - timedelta(days=1), paid_tax_pln=paid_pln)


def newDividend(when: date, dividend_pln: int = 0, tax_pln: int = 0) -> DividendItemPLN:
    dividend = DividendItem(received_dividend=Money(200, "USD"), paid_tax=Money(10, "USD"), date=when)
    return DividendItemPLN(
        source=dividend,
        dividend_pln_quotation_date=when - timedelta(days=1),
        received_dividend_pln=dividend_pln,
        tax_pln_quotation_date=when - timedelta(days=1),
        paid_tax_pln=tax_pln,
    )
