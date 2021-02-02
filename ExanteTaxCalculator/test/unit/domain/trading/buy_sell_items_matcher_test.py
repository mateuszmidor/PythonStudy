import unittest
from datetime import date
from money import Money
from decimal import Decimal

from src.utils.capture_exception import capture_exception
from src.domain.trading.buy_sell_items_matcher import BuySellItemsMatcher
from src.domain.transactions.buy_item import BuyItem
from src.domain.transactions.sell_item import SellItem
from src.domain.errors import InsufficientAssetError


def newBuy(name: str, amount: int, paid: Money, commission: Money, date: date, transaction_id: int) -> BuyItem:
    return BuyItem(
        date=date,
        transaction_id=transaction_id,
        asset_name=name,
        amount=amount,
        paid=paid,
        commission=commission,
    )


class TraderTest(unittest.TestCase):
    def test_trader_starts_with_empty_report(self):
        # given
        matcher = BuySellItemsMatcher()

        # when
        buy_sell_pairs = matcher.buy_sell_pairs

        # then
        self.assertEqual(len(buy_sell_pairs), 0)

    def test_sell_more_than_available_raises_error(self):
        # given
        matcher = BuySellItemsMatcher()

        # when
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        e = capture_exception(matcher.sell, sell_item)

        # then
        self.assertIsInstance(e, InsufficientAssetError)

    def test_buy10_sell10(self):
        """ Scenario1 """

        # given
        matcher = BuySellItemsMatcher()
        buy_item = newBuy("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        sell_item = SellItem("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 2)

        # when
        matcher.buy(buy_item)
        matcher.sell(sell_item)

        # then
        item = matcher.buy_sell_pairs[0]
        self.assertEqual(item.buy, buy_item)
        self.assertEqual(item.sell, sell_item)
        self.assertEqual(item.amount_sold, Decimal(10))

    def test_buy20_sell10(self):
        """ Scenario2 """

        # given
        matcher = BuySellItemsMatcher()
        buy_item = newBuy("PHYS", 20, Money("2000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        sell_item = SellItem("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 2)

        # when
        matcher.buy(buy_item)
        matcher.sell(sell_item)

        # then
        item = matcher.buy_sell_pairs[0]
        self.assertEqual(item.buy, buy_item)
        self.assertEqual(item.sell, sell_item)
        self.assertEqual(item.amount_sold, Decimal(10))

    def test_buy20_sell10_sell10(self):
        """ Scenario3 """

        # given
        matcher = BuySellItemsMatcher()
        buy_item = newBuy("PHYS", 20, Money("2000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        sell_item_1 = SellItem("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 2)
        sell_item_2 = SellItem("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 3)

        # when
        matcher.buy(buy_item)
        matcher.sell(sell_item_1)
        matcher.sell(sell_item_2)

        # then
        item = matcher.buy_sell_pairs[0]
        self.assertEqual(item.buy, buy_item)
        self.assertEqual(item.sell, sell_item_1)
        self.assertEqual(item.amount_sold, Decimal(10))
        item = matcher.buy_sell_pairs[1]
        self.assertEqual(item.buy, buy_item)
        self.assertEqual(item.sell, sell_item_2)
        self.assertEqual(item.amount_sold, Decimal(10))

    def test_buy15_buy15_sell10_sell10_sell10(self):
        """ Scenario4 """

        # given
        matcher = BuySellItemsMatcher()
        buy_item_1 = newBuy("PHYS", 15, Money("1500", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        buy_item_2 = newBuy("PHYS", 15, Money("1500", "USD"), Money("1", "USD"), date(2000, 10, 20), 2)
        sell_item_1 = SellItem("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 3)
        sell_item_2 = SellItem("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 4)
        sell_item_3 = SellItem("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 5)

        # when
        matcher.buy(buy_item_1)
        matcher.buy(buy_item_2)
        matcher.sell(sell_item_1)
        matcher.sell(sell_item_2)
        matcher.sell(sell_item_3)

        # then
        item = matcher.buy_sell_pairs[0]
        self.assertEqual(item.buy, buy_item_1)
        self.assertEqual(item.sell, sell_item_1)
        self.assertEqual(item.amount_sold, Decimal(10))
        item = matcher.buy_sell_pairs[1]
        self.assertEqual(item.buy, buy_item_1)
        self.assertEqual(item.sell, sell_item_2)
        self.assertEqual(item.amount_sold, Decimal(5))
        item = matcher.buy_sell_pairs[2]
        self.assertEqual(item.buy, buy_item_2)
        self.assertEqual(item.sell, sell_item_2)
        self.assertEqual(item.amount_sold, Decimal(5))
        item = matcher.buy_sell_pairs[3]
        self.assertEqual(item.buy, buy_item_2)
        self.assertEqual(item.sell, sell_item_3)
        self.assertEqual(item.amount_sold, Decimal(10))

    def test_buy10_buy10_sell20(self):
        """ Scenario5 """

        # given
        matcher = BuySellItemsMatcher()
        buy_item_1 = newBuy("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        buy_item_2 = newBuy("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 2)
        sell_item_1 = SellItem("PHYS", 20, Money("2000", "USD"), Money("1", "USD"), date(2000, 10, 30), 3)

        # when
        matcher.buy(buy_item_1)
        matcher.buy(buy_item_2)
        matcher.sell(sell_item_1)

        # then
        item = matcher.buy_sell_pairs[0]
        self.assertEqual(item.buy, buy_item_1)
        self.assertEqual(item.sell, sell_item_1)
        self.assertEqual(item.amount_sold, Decimal(10))
        item = matcher.buy_sell_pairs[1]
        self.assertEqual(item.buy, buy_item_2)
        self.assertEqual(item.sell, sell_item_1)
        self.assertEqual(item.amount_sold, Decimal(10))

    def test_buy10_buy10_buy10_sell15_sell15(self):
        """ Scenario6 """

        # given
        matcher = BuySellItemsMatcher()
        buy_item_1 = newBuy("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        buy_item_2 = newBuy("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 2)
        buy_item_3 = newBuy("PHYS", 10, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 3)
        sell_item_1 = SellItem("PHYS", 15, Money("1500", "USD"), Money("1", "USD"), date(2000, 10, 30), 4)
        sell_item_2 = SellItem("PHYS", 15, Money("1500", "USD"), Money("1", "USD"), date(2000, 10, 30), 5)

        # when
        matcher.buy(buy_item_1)
        matcher.buy(buy_item_2)
        matcher.buy(buy_item_3)
        matcher.sell(sell_item_1)
        matcher.sell(sell_item_2)

        # then
        item = matcher.buy_sell_pairs[0]
        self.assertEqual(item.buy, buy_item_1)
        self.assertEqual(item.sell, sell_item_1)
        self.assertEqual(item.amount_sold, Decimal(10))
        item = matcher.buy_sell_pairs[1]
        self.assertEqual(item.buy, buy_item_2)
        self.assertEqual(item.sell, sell_item_1)
        self.assertEqual(item.amount_sold, Decimal(5))
        item = matcher.buy_sell_pairs[2]
        self.assertEqual(item.buy, buy_item_2)
        self.assertEqual(item.sell, sell_item_2)
        self.assertEqual(item.amount_sold, Decimal(5))
        item = matcher.buy_sell_pairs[3]
        self.assertEqual(item.buy, buy_item_3)
        self.assertEqual(item.sell, sell_item_2)
        self.assertEqual(item.amount_sold, Decimal(10))
