import unittest
from money import Money
from datetime import date, timedelta

from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.profit_item import ProfitPLN
from src.domain.transactions import *
from src.domain.reporting.trade_report_builder import TradeReportBuilder
from utils import newProfit, newDividend, newTax


class TradeReportBuilderTest(unittest.TestCase):
    def test_report_items_get_sorted_by_date_ascending(self):
        # given
        profit1 = newProfit(date(2020, 2, 2))
        profit2 = newProfit(date(2020, 6, 2))
        dividend1 = newDividend(date(2020, 4, 2))
        dividend2 = newDividend(date(2020, 8, 2))
        tax1 = newTax(date(2020, 3, 2))
        tax2 = newTax(date(2020, 9, 2))

        # when
        items = TradeReportBuilder.build(
            profits=[profit1, profit2],
            dividends=[dividend1, dividend2],
            taxes=[tax1, tax2],
        )

        # then
        self.assertEqual(len(items), 6)
        self.assertEqual(items[0], profit1)
        self.assertEqual(items[1], tax1)
        self.assertEqual(items[2], dividend1)
        self.assertEqual(items[3], profit2)
        self.assertEqual(items[4], dividend2)
        self.assertEqual(items[5], tax2)
