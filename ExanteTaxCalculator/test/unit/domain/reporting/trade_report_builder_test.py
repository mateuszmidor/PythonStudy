import unittest
from money import Money
from datetime import datetime, timedelta

from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.profit_item import ProfitPLN
from src.domain.transactions import *
from src.domain.reporting.trading_report_builder import TradingReportBuilder
from src.domain.tax_declaration.tax_declaration_numbers import TaxDeclarationNumbers
from test.unit.domain.reporting.utils import newProfit, newDividend, newTax


class TradingReportBuilderTest(unittest.TestCase):
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
        report = TradingReportBuilder.build(
            profits=[profit1, profit2],
            dividends=[dividend1, dividend2],
            taxes=[tax1, tax2],
            results=TaxDeclarationNumbers(),
        )

        # then
        self.assertEqual(len(report.dividends), 2)
        self.assertEqual(report.dividends[0], dividend1)
        self.assertEqual(report.dividends[1], dividend2)

        self.assertEqual(len(report.taxes), 2)
        self.assertEqual(report.taxes[0], tax1)
        self.assertEqual(report.taxes[1], tax2)

        self.assertEqual(len(report.trades_by_asset[asset]), 2)
        self.assertEqual(report.trades_by_asset[asset][0], profit1)
        self.assertEqual(report.trades_by_asset[asset][1], profit2)

    def test_dividend_taxes_not_in_report(self):
        """ Dividend taxes should be passed on "taxes" list, the dividend.tax_paid_pln should not be considered """

        # given
        dividend1 = newDividend(when=datetime(2020, 4, 2), dividend_pln=80, tax_pln=8)
        dividend2 = newDividend(when=datetime(2020, 8, 2), dividend_pln=20, tax_pln=2)

        # when
        report = TradingReportBuilder.build(
            profits=[],
            dividends=[dividend1, dividend2],
            taxes=[],
            results=TaxDeclarationNumbers(),
        )

        # then
        self.assertEqual(len(report.dividends), 2)
        self.assertEqual(report.dividends[0], dividend1)
        self.assertEqual(report.dividends[1], dividend2)

        self.assertEqual(report.taxes, [])

        self.assertEqual(report.trades_by_asset, {})