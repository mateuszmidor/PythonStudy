from money import Money
from decimal import Decimal
from datetime import date, datetime, timedelta

from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.profit_item import ProfitPLN
from src.domain.transactions import *


def yesterday(when: datetime) -> date:
    return (when - timedelta(days=1)).date()


def newProfit(when: datetime, what="PHYS", paid_pln: int = 0, received_pln: int = 0) -> ProfitPLN:
    dummy_buy = BuyItem(asset_name=what, amount=Decimal(10), paid=Money(1000, "USD"), commission=Money(1, "USD"), date=datetime(2020, 1, 2))
    dummy_sell = SellItem(asset_name=what, amount=Decimal(10), received=Money(1000, "USD"), commission=Money(1, "USD"), date=when)
    buy_sell = BuySellPair(buy=dummy_buy, sell=dummy_sell, amount_sold=Decimal(0))
    dummy_buy_sell_pln = BuySellPairPLN(  # not important for reporting
        source=buy_sell,
        buy_pln_quotation_date=date(2020, 1, 1),
        buy_paid_pln=Decimal(3000),
        buy_commission_pln=Decimal(3),
        sell_pln_quotation_date=yesterday(when),
        sell_received_pln=Decimal(3000),
        sell_commission_pln=Decimal(3),
    )
    return ProfitPLN(source=dummy_buy_sell_pln, paid=paid_pln, received=Decimal(received_pln))


def newTax(when: datetime, paid_pln: int = 0) -> TaxItemPLN:
    dumm_tax = TaxItem(paid_tax=Money(0, "USD"), date=when)  # not important for reporting
    return TaxItemPLN(source=dumm_tax, tax_pln_quotation_date=yesterday(when), paid_tax_pln=Decimal(paid_pln))


def newDividend(when: datetime, dividend_pln: int = 0, tax_pln: int = 0) -> DividendItemPLN:
    dummy_dividend = DividendItem(received_dividend=Money(0, "USD"), paid_tax=None, date=when)  # not important for reporting
    dummy_tax = TaxItem(paid_tax=Decimal(0), date=when)  # not important for reporting
    paid_tax_pln = TaxItemPLN(source=dummy_tax, tax_pln_quotation_date=yesterday(when), paid_tax_pln=Decimal(tax_pln)) if tax_pln > 0 else None
    return DividendItemPLN(
        source=dummy_dividend,
        dividend_pln_quotation_date=yesterday(when),
        received_dividend_pln=Decimal(dividend_pln),
        paid_tax_pln=paid_tax_pln,
    )
