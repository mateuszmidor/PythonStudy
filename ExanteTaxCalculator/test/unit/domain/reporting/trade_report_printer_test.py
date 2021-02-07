import unittest
from money import Money
from datetime import date, timedelta

from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.profit_item import ProfitPLN
from src.domain.transactions import *
from src.domain.reporting.trade_report_printer import TradeReportPrinter
from utils import newProfit, newDividend, newTax


class TradeReportPrinterTest(unittest.TestCase):
    def test_print_profit(self):
        # given
        profit = newProfit(paid_pln=600, received_pln=300, when=date(2020, 2, 2))
        printer = TradeReportPrinter()

        # when
        report_strings = printer.to_strings([profit])

        # then
        self.assertEqual(len(report_strings), 1)
        self.assertTrue("BUY/SELL" in report_strings[0])
        self.assertTrue("-300.0000 PLN" in report_strings[0])
        self.assertTrue("02-02-2020" in report_strings[0])

    def test_print_tax(self):
        # given
        tax = newTax(paid_pln=45, when=date(2020, 5, 20))
        printer = TradeReportPrinter()

        # when
        report_strings = printer.to_strings([tax])

        # then
        self.assertEqual(len(report_strings), 1)
        self.assertTrue("TAX" in report_strings[0])
        self.assertTrue("45.0000 PLN" in report_strings[0])
        self.assertTrue("20-05-2020" in report_strings[0])

    def test_print_dividend(self):
        # given
        dividend = newDividend(dividend_pln=100, when=date(2020, 4, 2), tax_pln=15)
        printer = TradeReportPrinter()

        # when
        report_strings = printer.to_strings([dividend])

        # then
        self.assertEqual(len(report_strings), 2)
        self.assertTrue("DIVIDEND" in report_strings[0])
        self.assertTrue("100.0000 PLN" in report_strings[0])
        self.assertTrue("02-04-2020" in report_strings[0])
        self.assertTrue("TAX" in report_strings[1])
        self.assertTrue("15.0000 PLN" in report_strings[1])
        self.assertTrue("02-04-2020" in report_strings[1])
