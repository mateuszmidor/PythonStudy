import unittest
from money import Money
from datetime import date

from src.utils.capture_exception import capture_exception
from src.domain.buy_sell_items_matcher import BuySellItemsMatcher
from src.domain.transaction_items.buy_item import BuyItem
from src.domain.transaction_items.sell_item import SellItem
from src.domain.errors import InsufficientAssetError


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

    def test_buy1_sell1_gives_single_tax_report_item(self):
        # given
        matcher = BuySellItemsMatcher()

        # when
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        matcher.buy(buy_item)
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 2)
        matcher.sell(sell_item)
        buy_sell_pairs = matcher.buy_sell_pairs

        # then
        self.assertEqual(len(buy_sell_pairs), 1)
        item = buy_sell_pairs[0]
        self.assertEqual(item.asset_name, "PHYS")

        self.assertEqual(item.buy_amount, 100)
        self.assertEqual(item.buy_paid, Money("1000", "USD"))
        self.assertEqual(item.buy_commission, Money("1", "USD"))
        self.assertEqual(item.buy_date, date(2000, 10, 20))
        self.assertEqual(item.buy_transaction_id, 1)

        self.assertEqual(item.sell_amount, 100)
        self.assertEqual(item.sell_received, Money("1000", "USD"))
        self.assertEqual(item.sell_commission, Money("1", "USD"))
        self.assertEqual(item.sell_date, date(2000, 10, 30))
        self.assertEqual(item.sell_transaction_id, 2)

    def test_buy2_sell1_gives_two_tax_report_items(self):
        # given
        matcher = BuySellItemsMatcher()

        # when
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        matcher.buy(buy_item)
        buy_item = BuyItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 21), 2)
        matcher.buy(buy_item)

        sell_item = SellItem("PHYS", 150, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 3)
        matcher.sell(sell_item)
        buy_sell_pairs = matcher.buy_sell_pairs

        # then
        self.assertEqual(len(buy_sell_pairs), 2)

        item = buy_sell_pairs[0]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 1)
        self.assertEqual(item.sell_amount, 100)
        self.assertEqual(item.sell_transaction_id, 3)

        item = buy_sell_pairs[1]
        self.assertEqual(item.buy_transaction_id, 2)
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 3)

    def test_buy1_sell2_gives_two_tax_report_items(self):
        # given
        matcher = BuySellItemsMatcher()

        # when
        buy_item = BuyItem("PHYS", 150, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 11)
        matcher.buy(buy_item)

        sell_item = SellItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 12)
        matcher.sell(sell_item)
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 12, 31), 13)
        matcher.sell(sell_item)
        buy_sell_pairs = matcher.buy_sell_pairs

        # then
        self.assertEqual(len(buy_sell_pairs), 2)

        item = buy_sell_pairs[0]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 11)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 12)

        item = buy_sell_pairs[1]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 11)
        self.assertEqual(item.sell_amount, 100)
        self.assertEqual(item.sell_transaction_id, 13)

    def test_buy2_sell2_gives_three_tax_report_items(self):
        # given
        matcher = BuySellItemsMatcher()

        # when
        buy_item = BuyItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        matcher.buy(buy_item)
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 21), 2)
        matcher.buy(buy_item)

        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 3)
        matcher.sell(sell_item)
        sell_item = SellItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 12, 31), 4)
        matcher.sell(sell_item)
        buy_sell_pairs = matcher.buy_sell_pairs

        # then
        self.assertEqual(len(buy_sell_pairs), 3)

        item = buy_sell_pairs[0]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 1)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 3)

        item = buy_sell_pairs[1]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 2)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 3)

        item = buy_sell_pairs[2]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 2)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 4)