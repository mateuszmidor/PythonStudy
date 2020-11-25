import unittest
from money import Money
from decimal import Decimal
from tax_calculator import TaxCalculator

class TaxCalculatorTest(unittest.TestCase):
    def test_funding_results_in_currency_increase(self):
        # given
        calc = TaxCalculator()

        # when 
        m = Money(amount='100', currency='EUR')
        calc.fund(m)

        # then
        trading_report = calc.report()
        self.assertEqual(trading_report.get_currency("EUR"), Decimal("100.0"))

    def test_withdrawal_too_much_raises_exception(self):
        # given
        calc = TaxCalculator()

        # when
        m = Money(amount='100', currency='EUR')
        with self.assertRaises(ValueError):
            calc.withdraw(m)
    