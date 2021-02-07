import unittest
from money import Money
from decimal import Decimal
from src.domain.tax_calculator import TaxCalculator
from src.domain.profit_item import ProfitItem
from src.domain.transactions.dividend_item import DividendItem
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.utils.capture_exception import capture_exception

# date =
# def make_dividend(amount_pln: Decimal) -> DividendItemPLN:
#     d = DividendItem(received_dividend=Money(amount_pln, "PLN"), paid_tax=Money(tax_pln, "PLN"), date)
class TaxCalculatorTest(unittest.TestCase):
    def test_zero_profit_from_zero_items(self):
        # given
        calc = TaxCalculator(19)

        # when
        total_profit, total_cost, total_tax, paid_tax = calc.calc_profit_tax(
            buys=[],
            sells=[],
            dividends=[],
            taxes=[],
        )

        # then
        self.assertEqual(total_profit, Money("0", "PLN"))
        self.assertEqual(total_cost, Money("0", "PLN"))
        self.assertEqual(total_tax, Money("0", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

    def test_positive_profit_from_positive_buy_sell_items(self):
        # given
        calc = TaxCalculator(19)
        buy1 = Decimal(100)
        sell1 = Decimal(125)
        buy2 = Decimal(100)
        sell2 = Decimal(175)

        # when
        total_profit, total_cost, total_tax, paid_tax = calc.calc_profit_tax(
            buys=[buy1, buy2],
            sells=[sell1, sell2],
            dividends=[],
            taxes=[],
        )

        # then
        self.assertEqual(total_profit, Money("300", "PLN"))
        self.assertEqual(total_cost, Money("200", "PLN"))
        self.assertEqual(total_tax, Money("19", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

    def test_positive_profit_from_dividends_items(self):
        # given
        dividend1 = Decimal(20)
        dividend2 = Decimal(80)
        calc = TaxCalculator(19)

        # when
        total_profit, total_cost, total_tax, paid_tax = calc.calc_profit_tax(
            buys=[],
            sells=[],
            dividends=[dividend1, dividend2],
            taxes=[],
        )

        # then
        self.assertEqual(total_profit, Money("100", "PLN"))
        self.assertEqual(total_cost, Money("0", "PLN"))
        self.assertEqual(total_tax, Money("19", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

    def test_paid_tax_from_tax_items(self):
        # given
        tax1 = Decimal(20)
        tax2 = Decimal(80)
        calc = TaxCalculator(19)

        # when
        total_profit, total_cost, total_tax, paid_tax = calc.calc_profit_tax(
            buys=[],
            sells=[],
            dividends=[],
            taxes=[tax1, tax2],
        )

        # then
        self.assertEqual(total_profit, Money("0", "PLN"))
        self.assertEqual(total_cost, Money("0", "PLN"))
        self.assertEqual(total_tax, Money("0", "PLN"))
        self.assertEqual(paid_tax, Money("100", "PLN"))

    def test_no_tax_from_negative_buy_sell_items(self):
        # given
        buy1 = Decimal(125)
        sell1 = Decimal(100)
        buy2 = Decimal(75)
        sell2 = Decimal(50)
        calc = TaxCalculator(19)

        # when
        total_profit, total_cost, total_tax, paid_tax = calc.calc_profit_tax(buys=[buy1, buy2], sells=[sell1, sell2], dividends=[], taxes=[])

        # then
        self.assertEqual(total_profit, Money("150", "PLN"))
        self.assertEqual(total_cost, Money("200", "PLN"))
        self.assertEqual(total_tax, Money("0", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

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
        calc = TaxCalculator(19)

        # when
        total_profit, total_cost, total_tax, paid_tax = calc.calc_profit_tax(
            buys=[buy1, buy2],
            sells=[sell1, sell2],
            dividends=[dividend1, dividend2],
            taxes=[tax1, tax2],
        )

        # then
        self.assertEqual(total_profit, Money("375", "PLN"))
        self.assertEqual(total_cost, Money("225", "PLN"))
        self.assertEqual(total_tax, Money(150 * 0.19, "PLN"))
        self.assertEqual(paid_tax, Money("10", "PLN"))
