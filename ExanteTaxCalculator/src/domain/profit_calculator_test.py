import unittest
from money import Money
from datetime import date
from decimal import Decimal

from src.domain.profit_calculator import ProfitCalculator
from src.domain.taxable_item_quotator import TaxableItemPLNQuoted


def USD(amount: float) -> Money:
    return Money(str(amount), "USD")


def PLN(amount: float) -> Money:
    return Money(str(amount), "PLN")


class ProfitCalculatorTest(unittest.TestCase):
    def test_full_sell_profit(self):
        # given
        taxable = TaxableItemPLNQuoted(
            "PHYS",
            100,
            USD(1000),
            USD(1),
            date(2000, 12, 20),
            1,
            100,
            USD(1000),
            USD(1),
            date(2000, 12, 21),
            2,
            date(2000, 12, 19),
            Decimal(3000),
            Decimal(3),  # PLN/USD = 3
            date(2000, 12, 20),
            Decimal(4000),
            Decimal(4),  # PLN/USD = 4
        )
        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_profit = 4000 - 4 - (3000 + 3) * 100 / 100
        self.assertEqual(profit.profit, PLN(expected_profit))

    def test_half_sell_profit(self):
        # given
        taxable = TaxableItemPLNQuoted(
            "PHYS",
            100,
            USD(1000),
            USD(1),
            date(2000, 12, 20),
            1,
            50,
            USD(500),
            USD(1),
            date(2000, 12, 21),
            2,
            date(2000, 12, 19),
            Decimal(3000),
            Decimal(3),  # PLN/USD = 3
            date(2000, 12, 20),
            Decimal(2000),
            Decimal(4),  # PLN/USD = 4, half assets sold so 2000PLN received
        )
        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_profit = 2000 - 4 - (3000 + 3) * 50 / 100
        self.assertEqual(profit.profit, PLN(expected_profit))

    def test_quater_sell_profit(self):
        # given
        taxable = TaxableItemPLNQuoted(
            "PHYS",
            100,
            USD(1000),
            USD(1),
            date(2000, 12, 20),
            1,
            25,
            USD(250),
            USD(1),
            date(2000, 12, 21),
            2,
            date(2000, 12, 19),
            Decimal(3000),
            Decimal(3),  # PLN/USD = 3
            date(2000, 12, 20),
            Decimal(1000),
            Decimal(4),  # PLN/USD = 4, quater assets sold so 1000PLN received
        )
        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_profit = 1000 - 4 - (3000 + 3) * 25 / 100
        self.assertEqual(profit.profit, PLN(expected_profit))