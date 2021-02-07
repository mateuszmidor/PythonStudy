import unittest
from money import Money
from datetime import date
from decimal import Decimal

from src.domain.profit_calculator import ProfitCalculator
from src.domain.transactions.buy_item import BuyItem
from src.domain.transactions.sell_item import SellItem
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN


def USD(amount: float) -> Money:
    return Money(amount, "USD")


def PLN(amount: float) -> Money:
    return Money(amount, "PLN")


def newBuySellPLN(
    buy_amount,
    sell_amount,
    amount_sold: Decimal,
    buy_paid_pln,
    buy_commission_pln,
    sell_received_pln,
    sell_commission_pln: Decimal,
) -> BuySellPairPLN:
    return BuySellPairPLN(
        source=BuySellPair(
            buy=BuyItem(
                asset_name="-",
                amount=buy_amount,
                paid=USD(0),
                commission=USD(0),
            ),
            sell=SellItem(
                asset_name="-",
                amount=sell_amount,
                received=USD(0),
                commission=USD(0),
            ),
            amount_sold=amount_sold,
        ),
        buy_pln_quotation_date=date(2000, 12, 19),
        buy_paid_pln=buy_paid_pln,
        buy_commission_pln=buy_commission_pln,
        sell_pln_quotation_date=date(2000, 12, 20),
        sell_received_pln=sell_received_pln,
        sell_commission_pln=sell_commission_pln,
    )


class ProfitCalculatorTest(unittest.TestCase):
    def test_buy_100_sell_100_different_quotation(self):
        # given
        taxable = newBuySellPLN(
            buy_amount=100,
            sell_amount=100,
            amount_sold=100,
            buy_paid_pln=Decimal(3000),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_received_pln=Decimal(4000),  # PLN/USD = 4
            sell_commission_pln=Decimal(4),
        )

        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_paid = (3000 + 3) * 100 / 100
        expected_received = (4000 - 4) * 100 / 100
        self.assertEqual(profit.paid, PLN(expected_paid))
        self.assertEqual(profit.received, PLN(expected_received))

    def test_buy_100_sell_50_different_quotation(self):
        # given
        taxable = newBuySellPLN(
            buy_amount=100,
            sell_amount=50,
            amount_sold=50,
            buy_paid_pln=Decimal(3000),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_received_pln=Decimal(2000),  # PLN/USD = 4
            sell_commission_pln=Decimal(4),
        )

        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_paid = (3000 + 3) * 50 / 100
        expected_received = (2000 - 4) * 50 / 50
        self.assertEqual(profit.paid, PLN(expected_paid))
        self.assertEqual(profit.received, PLN(expected_received))

    def test_buy_50_sell_100_different_quotation(self):
        # given
        taxable = newBuySellPLN(
            buy_amount=50,
            sell_amount=100,
            amount_sold=50,
            buy_paid_pln=Decimal(1500),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_received_pln=Decimal(4000),  # PLN/USD = 4
            sell_commission_pln=Decimal(4),
        )

        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_paid = (1500 + 3) * 50 / 50
        expected_received = (4000 - 4) * 50 / 100
        self.assertEqual(profit.paid, PLN(expected_paid))
        self.assertEqual(profit.received, PLN(expected_received))

    def test_buy_100_sell_200_sold_25_different_quotation(self):
        # given
        taxable = newBuySellPLN(
            buy_amount=100,
            sell_amount=200,
            amount_sold=25,
            buy_paid_pln=Decimal(3000),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_received_pln=Decimal(8000),  # PLN/USD = 4
            sell_commission_pln=Decimal(4),
        )

        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_paid = (3000 + 3) * 25 / 100
        expected_received = (8000 - 4) * 25 / 200
        self.assertEqual(profit.paid, PLN(expected_paid))
        self.assertEqual(profit.received, PLN(expected_received))

    def test_buy_200_sell_100_sold_25_different_quotation(self):
        # given
        taxable = newBuySellPLN(
            buy_amount=200,
            sell_amount=100,
            amount_sold=25,
            buy_paid_pln=Decimal(6000),  # PLN/USD = 3
            buy_commission_pln=Decimal(3),
            sell_received_pln=Decimal(4000),  # PLN/USD = 4
            sell_commission_pln=Decimal(4),
        )

        calculator = ProfitCalculator()

        # when
        profit = calculator.calc_profit(taxable)

        # then
        expected_paid = (6000 + 3) * 25 / 200
        expected_received = (4000 - 4) * 25 / 100
        self.assertEqual(profit.paid, PLN(expected_paid))
        self.assertEqual(profit.received, PLN(expected_received))
