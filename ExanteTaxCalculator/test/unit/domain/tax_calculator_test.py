import unittest
from money import Money
from decimal import Decimal
from src.domain.tax_calculator import TaxCalculator
from src.domain.profit_item import ProfitItem
from src.utils.capture_exception import capture_exception
from src.domain.currency import EUR

class TaxCalculatorTest(unittest.TestCase):

    def test_zero_profit_from_zero_items(self):
        # given
        calc = TaxCalculator(19)

        # when
        total_profit, total_tax = calc.calc_profit_tax([])

        # then
        self.assertEqual(total_profit, Money("0", "PLN"))
        self.assertEqual(total_tax, Money("0", "PLN"))

    def test_positive_profit_from_positive_items(self):
        # given
        calc = TaxCalculator(19)
        profit1 = ProfitItem(Decimal(25))
        profit2 = ProfitItem(Decimal(75))

        # when
        total_profit, total_tax = calc.calc_profit_tax([profit1, profit2])

        # then
        self.assertEqual(total_profit, Money("100", "PLN"))
        self.assertEqual(total_tax, Money("19", "PLN"))

    def test_positive_little_profit_from_positive_little_items(self):
        # given
        calc = TaxCalculator(19)
        profit1 = ProfitItem(Decimal("0.25"))
        profit2 = ProfitItem(Decimal("0.75"))

        # when
        total_profit, total_tax = calc.calc_profit_tax([profit1, profit2])

        # then
        self.assertEqual(total_profit, Money("1.00", "PLN"))
        self.assertEqual(total_tax, Money("0.19", "PLN"))

    def test_negative_profit_from_negative_items(self):
        # given
        calc = TaxCalculator(19)
        profit1 = ProfitItem(Decimal(25))
        profit2 = ProfitItem(Decimal(-75))

        # when
        total_profit, total_tax = calc.calc_profit_tax([profit1, profit2])

        # then
        self.assertEqual(total_profit, Money("-50", "PLN"))
        self.assertEqual(total_tax, Money("0.00", "PLN"))

    def test_little_negative_profit_from_little_negative_items(self):
        # given
        calc = TaxCalculator(19)
        profit1 = ProfitItem(Decimal("0.25"))
        profit2 = ProfitItem(Decimal("-0.75"))

        # when
        total_profit, total_tax = calc.calc_profit_tax([profit1, profit2])

        # then
        self.assertEqual(total_profit, Money("-0.50", "PLN"))
        self.assertEqual(total_tax, Money("0.00", "PLN"))