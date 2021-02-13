import unittest
from money import Money
from decimal import Decimal
from src.domain.tax_calculator import TaxCalculator
from src.domain.profit_item import ProfitItem
from src.domain.transactions.dividend_item import DividendItem
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.utils.capture_exception import capture_exception


TAX_PERCENTAGE = Decimal(19.0)


def calc_tax(amount_pln: Decimal) -> Money:
    return PLN(amount_pln * TAX_PERCENTAGE / 100)


def PLN(amount: Decimal) -> Money:
    return Money(amount, "PLN")


class TaxCalculatorTest(unittest.TestCase):
    def test_zero_profit_from_zero_items(self):
        # given
        calc = TaxCalculator(TAX_PERCENTAGE)

        # when
        result = calc.calc_profit_tax(
            buys=[],
            sells=[],
            dividends=[],
            taxes=[],
        )

        # then
        self.assertEqual(result.shares_total_cost, PLN(0))
        self.assertEqual(result.shares_total_income, PLN(0))
        self.assertEqual(result.shares_total_tax, PLN(0))
        self.assertEqual(result.dividends_total_income, PLN(0))
        self.assertEqual(result.dividends_total_tax, PLN(0))
        self.assertEqual(result.dividends_tax_already_paid, PLN(0))
        self.assertEqual(result.dividends_tax_yet_to_be_paid, PLN(0))

    def test_positive_profit_from_positive_buy_sell_items(self):
        # given
        calc = TaxCalculator(TAX_PERCENTAGE)
        buy1 = Decimal(100)
        sell1 = Decimal(125)
        buy2 = Decimal(100)
        sell2 = Decimal(175)

        # when
        result = calc.calc_profit_tax(
            buys=[buy1, buy2],
            sells=[sell1, sell2],
            dividends=[],
            taxes=[],
        )

        # then
        self.assertEqual(result.shares_total_cost, PLN(200))
        self.assertEqual(result.shares_total_income, PLN(300))
        self.assertEqual(result.shares_total_tax, calc_tax(100))
        self.assertEqual(result.dividends_total_income, PLN(0))
        self.assertEqual(result.dividends_total_tax, PLN(0))
        self.assertEqual(result.dividends_tax_already_paid, PLN(0))
        self.assertEqual(result.dividends_tax_yet_to_be_paid, PLN(0))

    def test_positive_profit_from_dividends_items(self):
        # given
        dividend1 = Decimal(20)
        dividend2 = Decimal(80)
        calc = TaxCalculator(TAX_PERCENTAGE)

        # when
        result = calc.calc_profit_tax(
            buys=[],
            sells=[],
            dividends=[dividend1, dividend2],
            taxes=[],
        )

        # then
        self.assertEqual(result.shares_total_cost, PLN(0))
        self.assertEqual(result.shares_total_income, PLN(0))
        self.assertEqual(result.shares_total_tax, PLN(0))
        self.assertEqual(result.dividends_total_income, PLN(100))
        self.assertEqual(result.dividends_total_tax, calc_tax(100))
        self.assertEqual(result.dividends_tax_already_paid, PLN(0))
        self.assertEqual(result.dividends_tax_yet_to_be_paid, calc_tax(100))

    def test_paid_tax_from_tax_items(self):
        # given
        tax1 = Decimal(20)
        tax2 = Decimal(80)
        calc = TaxCalculator(TAX_PERCENTAGE)

        # when
        result = calc.calc_profit_tax(
            buys=[],
            sells=[],
            dividends=[],
            taxes=[tax1, tax2],
        )

        # then
        self.assertEqual(result.shares_total_cost, PLN(0))
        self.assertEqual(result.shares_total_income, PLN(0))
        self.assertEqual(result.shares_total_tax, PLN(0))
        self.assertEqual(result.dividends_total_income, PLN(0))
        self.assertEqual(result.dividends_total_tax, PLN(0))
        self.assertEqual(result.dividends_tax_already_paid, PLN(100))
        self.assertEqual(result.dividends_tax_yet_to_be_paid, PLN(0))

    def test_no_tax_from_negative_buy_sell_items(self):
        # given
        buy1 = Decimal(125)
        sell1 = Decimal(100)
        buy2 = Decimal(75)
        sell2 = Decimal(50)
        calc = TaxCalculator(TAX_PERCENTAGE)

        # when
        result = calc.calc_profit_tax(
            buys=[buy1, buy2],
            sells=[sell1, sell2],
            dividends=[],
            taxes=[],
        )

        # then
        self.assertEqual(result.shares_total_cost, PLN(200))
        self.assertEqual(result.shares_total_income, PLN(150))
        self.assertEqual(result.shares_total_tax, PLN(0))
        self.assertEqual(result.dividends_total_income, PLN(0))
        self.assertEqual(result.dividends_total_tax, PLN(0))
        self.assertEqual(result.dividends_tax_already_paid, PLN(0))
        self.assertEqual(result.dividends_tax_yet_to_be_paid, PLN(0))

    def test_all_items_items(self):
        # given
        buy1 = Decimal(125)
        sell1 = Decimal(100)
        buy2 = Decimal(100)
        sell2 = Decimal(175)
        dividend1 = Decimal(20)
        dividend2 = Decimal(80)
        tax1 = Decimal(3)
        tax2 = Decimal(7)
        calc = TaxCalculator(TAX_PERCENTAGE)

        # when
        result = calc.calc_profit_tax(
            buys=[buy1, buy2],
            sells=[sell1, sell2],
            dividends=[dividend1, dividend2],
            taxes=[tax1, tax2],
        )

        # then
        self.assertEqual(result.shares_total_cost, PLN(225))
        self.assertEqual(result.shares_total_income, PLN(275))
        self.assertEqual(result.shares_total_tax, calc_tax(50))
        self.assertEqual(result.dividends_total_income, PLN(100))
        self.assertEqual(result.dividends_total_tax, calc_tax(100))
        self.assertEqual(result.dividends_tax_already_paid, PLN(10))
        self.assertEqual(result.dividends_tax_yet_to_be_paid, calc_tax(100) - 10)
