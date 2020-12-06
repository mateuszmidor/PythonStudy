import unittest
from money import Money
from datetime import date

from src.utils.capture_exception import capture_exception
from src.domain.trader import Trader
from src.domain.buy_item import BuyItem
from src.domain.sell_item import SellItem

class TraderTest(unittest.TestCase):
    def test_trader_starts_with_empty_report(self):
        # given
        trader = Trader()

        # when
        report = trader.report()

        # then
        self.assertEqual(len(report.items), 0)


    def test_sell_more_than_available_raises_error(self):
        # given
        trader = Trader()

        # when
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20))
        e = capture_exception(trader.sell, sell_item)
        
        # then
        self.assertIsInstance(e, ValueError)


    def test_buy1_sell1_gives_single_tax_report_item(self):
        # given
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20))
        trader.buy(buy_item)
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30))
        trader.sell(sell_item)
        report = trader.report()

        # then
        self.assertEqual(len(report.items), 1)
        item = report.items[0]
        self.assertEqual(item.buy_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 100)


    def test_buy2_sell1_gives_two_tax_report_items(self):
        # given
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20))
        trader.buy(buy_item)
        buy_item = BuyItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 21))
        trader.buy(buy_item)

        sell_item = SellItem("PHYS", 150, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30))
        trader.sell(sell_item)
        report = trader.report()

        # then
        self.assertEqual(len(report.items), 2)
        
        item = report.items[0]
        self.assertEqual(item.sell_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 100)

        item = report.items[1]
        self.assertEqual(item.sell_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 50)


    def test_buy1_sell2_gives_two_tax_report_items(self):
        # given
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 150, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20))
        trader.buy(buy_item)

        sell_item = SellItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30))
        trader.sell(sell_item)
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 12, 31))
        trader.sell(sell_item)
        report = trader.report()

        # then
        self.assertEqual(len(report.items), 2)
        
        item = report.items[0]
        self.assertEqual(item.sell_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 50)
        self.assertEqual(item.buy_item.asset_left, 100)

        item = report.items[1]
        self.assertEqual(item.sell_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 100)
        self.assertEqual(item.buy_item.asset_left, 0)


    def test_buy2_sell2_gives_three_tax_report_items(self):
        # given
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20))
        trader.buy(buy_item)
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 21))
        trader.buy(buy_item)

        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30))
        trader.sell(sell_item)
        sell_item = SellItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 12, 31))
        trader.sell(sell_item)
        report = trader.report()

        # then
        self.assertEqual(len(report.items), 3)
        
        item = report.items[0]
        self.assertEqual(item.sell_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 50)
        self.assertEqual(item.buy_item.asset_left, 0)

        item = report.items[1]
        self.assertEqual(item.sell_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 50)
        self.assertEqual(item.buy_item.asset_left, 50)

        item = report.items[2]
        self.assertEqual(item.sell_item.asset_name, "PHYS")
        self.assertEqual(item.sell_item.amount, 50)
        self.assertEqual(item.buy_item.asset_left, 0)