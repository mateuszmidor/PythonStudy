import unittest
from money import Money
from decimal import Decimal
from src.domain.tax_calculator import TaxCalculator
from src.utils.capture_exception import capture_exception
from src.domain.currency import EUR

class TaxCalculatorTest(unittest.TestCase):
    def test_funding_results_in_currency_increase(self):
        # given
        calc = TaxCalculator()

        # when 
        m = Money(amount='100', currency='EUR')
        calc.fund(m)
    
        # then
        eur_owned = calc.report().get_currency(EUR)
        self.assertEqual(eur_owned, Decimal("100.0"))

    def test_withdrawal_too_much_raises_exception(self):
        # given
        calc = TaxCalculator()

        # when
        m = Money(amount='100', currency='EUR')
        e = capture_exception(calc.withdraw, m)

        # then
        self.assertIsInstance(e, ValueError)