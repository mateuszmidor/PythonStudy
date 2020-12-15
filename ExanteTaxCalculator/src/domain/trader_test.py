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
        taxable_items = trader.taxable_items()

        # then
        self.assertEqual(len(taxable_items), 0)


    def test_sell_more_than_available_raises_error(self):
        # given
        trader = Trader()

        # when
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        e = capture_exception(trader.sell, sell_item)
        
        # then
        self.assertIsInstance(e, ValueError)


    def test_buy1_sell1_gives_single_tax_report_item(self):
        # given
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        trader.buy(buy_item)
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 2)
        trader.sell(sell_item)
        taxable_items = trader.taxable_items()

        # then
        self.assertEqual(len(taxable_items), 1)
        item = taxable_items[0]
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
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        trader.buy(buy_item)
        buy_item = BuyItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 21), 2)
        trader.buy(buy_item)

        sell_item = SellItem("PHYS", 150, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 3)
        trader.sell(sell_item)
        taxable_items = trader.taxable_items()

        # then
        self.assertEqual(len(taxable_items), 2)
        
        item = taxable_items[0]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 1)
        self.assertEqual(item.sell_amount, 100)
        self.assertEqual(item.sell_transaction_id, 3)

        item = taxable_items[1]
        self.assertEqual(item.buy_transaction_id, 2)
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 3)


    def test_buy1_sell2_gives_two_tax_report_items(self):
        # given
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 150, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 11)
        trader.buy(buy_item)

        sell_item = SellItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 12)
        trader.sell(sell_item)
        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 12, 31), 13)
        trader.sell(sell_item)
        taxable_items = trader.taxable_items()

        # then
        self.assertEqual(len(taxable_items), 2)
        
        item = taxable_items[0]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 11)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 12)

        item = taxable_items[1]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 11)
        self.assertEqual(item.sell_amount, 100)
        self.assertEqual(item.sell_transaction_id, 13)


    def test_buy2_sell2_gives_three_tax_report_items(self):
        # given
        trader = Trader()

        # when
        buy_item = BuyItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 20), 1)
        trader.buy(buy_item)
        buy_item = BuyItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 21), 2)
        trader.buy(buy_item)

        sell_item = SellItem("PHYS", 100, Money("1000", "USD"), Money("1", "USD"), date(2000, 10, 30), 3)
        trader.sell(sell_item)
        sell_item = SellItem("PHYS", 50, Money("1000", "USD"), Money("1", "USD"), date(2000, 12, 31), 4)
        trader.sell(sell_item)
        taxable_items = trader.taxable_items()

        # then
        self.assertEqual(len(taxable_items), 3)
        
        item = taxable_items[0]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 1)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 3)

        item = taxable_items[1]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 2)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 3)

        item = taxable_items[2]
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.buy_transaction_id, 2)
        self.assertEqual(item.sell_amount, 50)
        self.assertEqual(item.sell_transaction_id, 4)