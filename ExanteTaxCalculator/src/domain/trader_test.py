import unittest
from src.domain.trader import Trader

class TraderTest(unittest.TestCase):
    def test_trader_starts_with_empty_report(self):
        # given
        trader = Trader()

        # when
        report = trader.report()

        # then
        self.assertEqual(len(report.items), 0)