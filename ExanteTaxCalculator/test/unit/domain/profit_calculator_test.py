import unittest
from money import Money
from datetime import date
from decimal import Decimal

from src.domain.profit_calculator import ProfitCalculator
from src.domain.buy_sell_pair_pln import BuySellPairPLN


def USD(amount: float) -> Money:
    return Money(str(amount), "USD")


def PLN(amount: float) -> Money:
    return Money(str(amount), "PLN")


class ProfitCalculatorTest(unittest.TestCase):
    def test_full_sell_profit(self):
        # given
        taxable = BuySellPairPLN(
            asset_name="PHYS",
            buy_amount=100,
            buy_paid=USD(1000),
            buy_commission=USD(1),
            buy_date=date(2000, 12, 20),
            buy_transaction_id=1,
            sell_amount=100,
            sell_received=USD(1000),
            sell_commission=USD(1),
            sell_date=date(2000, 12, 21),
            sell_transaction_id=2,
            buy_pln_quotation_date=date(2000, 12, 19),
            buy_paid_pln=Decimal(3000),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_pln_quotation_date=date(2000, 12, 20),
            sell_received_pln=Decimal(4000),  # PLN/USD = 4
            sell_commission_pln=Decimal(4),
        )
        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_profit = 4000 - 4 - (3000 + 3) * 100 / 100
        self.assertEqual(profit.profit, PLN(expected_profit))

    def test_half_sell_profit(self):
        # given
        taxable = BuySellPairPLN(
            asset_name="PHYS",
            buy_amount=100,
            buy_paid=USD(1000),
            buy_commission=USD(1),
            buy_date=date(2000, 12, 20),
            buy_transaction_id=1,
            sell_amount=50,
            sell_received=USD(500),
            sell_commission=USD(1),
            sell_date=date(2000, 12, 21),
            sell_transaction_id=2,
            buy_pln_quotation_date=date(2000, 12, 19),
            buy_paid_pln=Decimal(3000),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_pln_quotation_date=date(2000, 12, 20),
            sell_received_pln=Decimal(2000),  # PLN/USD = 4, half assets sold so 2000PLN received
            sell_commission_pln=Decimal(4),
        )
        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_profit = 2000 - 4 - (3000 + 3) * 50 / 100
        self.assertEqual(profit.profit, PLN(expected_profit))

    def test_quater_sell_profit(self):
        # given
        taxable = BuySellPairPLN(
            asset_name="PHYS",
            buy_amount=100,
            buy_paid=USD(1000),
            buy_commission=USD(1),
            buy_date=date(2000, 12, 20),
            buy_transaction_id=1,
            sell_amount=25,
            sell_received=USD(250),
            sell_commission=USD(1),
            sell_date=date(2000, 12, 21),
            sell_transaction_id=2,
            buy_pln_quotation_date=date(2000, 12, 19),
            buy_paid_pln=Decimal(3000),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_pln_quotation_date=date(2000, 12, 20),
            sell_received_pln=Decimal(1000),  # PLN/USD = 4, quater assets sold so 1000PLN received
            sell_commission_pln=Decimal(4),
        )
        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_profit = 1000 - 4 - (3000 + 3) * 25 / 100
        self.assertEqual(profit.profit, PLN(expected_profit))