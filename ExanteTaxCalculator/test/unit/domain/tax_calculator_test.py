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
        total_profit, total_tax, paid_tax = calc.calc_profit_tax(
            trades=[],
            dividends=[],
            taxes=[],
        )

        # then
        self.assertEqual(total_profit, Money("0", "PLN"))
        self.assertEqual(total_tax, Money("0", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

    def test_positive_profit_from_positive_buy_sell_items(self):
        # given
        calc = TaxCalculator(19)
        profit1 = Decimal(25)
        profit2 = Decimal(75)

        # when
        total_profit, total_tax, paid_tax = calc.calc_profit_tax(trades=[profit1, profit2], dividends=[], taxes=[])

        # then
        self.assertEqual(total_profit, Money("100", "PLN"))
        self.assertEqual(total_tax, Money("19", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

    def test_positive_profit_from_dividends_items(self):
        # given
        dividend1 = Decimal(20)
        dividend2 = Decimal(80)
        calc = TaxCalculator(19)

        # when
        total_profit, total_tax, paid_tax = calc.calc_profit_tax(
            trades=[],
            dividends=[dividend1, dividend2],
            taxes=[],
        )

        # then
        self.assertEqual(total_profit, Money("100", "PLN"))
        self.assertEqual(total_tax, Money("19", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

    def test_paid_tax_from_tax_items(self):
        # given
        tax1 = Decimal(20)
        tax2 = Decimal(80)
        calc = TaxCalculator(19)

        # when
        total_profit, total_tax, paid_tax = calc.calc_profit_tax(
            trades=[],
            dividends=[],
            taxes=[tax1, tax2],
        )

        # then
        self.assertEqual(total_profit, Money("0", "PLN"))
        self.assertEqual(total_tax, Money("0", "PLN"))
        self.assertEqual(paid_tax, Money("100", "PLN"))

    def test_negative_profit_from_negative_buy_sell_items(self):
        # given
        profit1 = Decimal(25)
        profit2 = Decimal(-75)
        calc = TaxCalculator(19)

        # when
        total_profit, total_tax, paid_tax = calc.calc_profit_tax(trades=[profit1, profit2], dividends=[], taxes=[])

        # then
        self.assertEqual(total_profit, Money("-50", "PLN"))
        self.assertEqual(total_tax, Money("0", "PLN"))
        self.assertEqual(paid_tax, Money("0", "PLN"))

    def test_all_items_items(self):
        # given
        profit1 = Decimal(25)
        profit2 = Decimal(-75)
        dividend1 = Decimal(20)
        dividend2 = Decimal(80)
        tax1 = Decimal(3)
        tax2 = Decimal(7)
        calc = TaxCalculator(19)

        # when
        total_profit, total_tax, paid_tax = calc.calc_profit_tax(
            trades=[profit1, profit2],
            dividends=[dividend1, dividend2],
            taxes=[tax1, tax2],
        )

        # then
        self.assertEqual(total_profit, Money("50", "PLN"))
        self.assertEqual(total_tax, Money(50 * 0.19, "PLN"))
        self.assertEqual(paid_tax, Money("10", "PLN"))
