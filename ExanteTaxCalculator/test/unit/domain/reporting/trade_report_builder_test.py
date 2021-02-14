import unittest
from money import Money
from datetime import datetime, timedelta

from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.profit_item import ProfitPLN
from src.domain.transactions import *
from src.domain.reporting.trade_report_builder import TradeReportBuilder
from src.domain.tax_calculator import CalculationResult
from utils import newProfit, newDividend, newTax


class TradeReportBuilderTest(unittest.TestCase):
    def test_report_items_get_sorted_by_date_ascending(self):
        # given
        asset = "PHYS"
        dividend1 = newDividend(datetime(2020, 4, 2), 80)
        dividend2 = newDividend(datetime(2020, 8, 2), 20)
        tax1 = newTax(datetime(2020, 3, 2), 20)
        tax2 = newTax(datetime(2020, 9, 2), 5)
        profit1 = newProfit(datetime(2020, 2, 2), asset, 1000, 1100)
        profit2 = newProfit(datetime(2020, 6, 2), asset, 300, 350)

        # when
        report = TradeReportBuilder.build(
            profits=[profit1, profit2],
            dividends=[dividend1, dividend2],
            taxes=[tax1, tax2],
            results=CalculationResult(),
        )

        # then
        self.assertEqual(len(report.dividends), 2)
        self.assertEqual(report.dividends[0], dividend1)
        self.assertEqual(report.dividends[1], dividend2)

        self.assertEqual(len(report.taxes), 2)
        self.assertEqual(report.taxes[0], tax1)
        self.assertEqual(report.taxes[1], tax2)

        self.assertEqual(len(report.profits[asset]), 2)
        self.assertEqual(report.profits[asset][0], profit1)
        self.assertEqual(report.profits[asset][1], profit2)
