import unittest
import datetime
from typing import Optional
from decimal import Decimal
from money import Money

from src.utils.capture_exception import capture_exception
from src.domain.buy_sell_pair import BuySellPair
from src.domain.currency import Currency
from src.domain.quotation.buy_sell_pair_pln_quotator import BuySellPairPLNQuotator
from src.domain.errors import NoQuotesAvailableError


class QuotesProviderStub:
    usd_table = {
        datetime.date(2000, 12, 20): 3.0,  # tuesday
        datetime.date(2000, 12, 21): 3.0,
        datetime.date(2000, 12, 22): 3.0,
        datetime.date(2000, 12, 23): 3.0,
        # datetime.date(2000, 12, 24) : 3.0, # saturday
        # datetime.date(2000, 12, 25) : 3.0, # sunday
        datetime.date(2000, 12, 26): 4.0,
        datetime.date(2000, 12, 27): 4.0,
    }

    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        if currency != Currency("USD"):
            return None
        if date not in QuotesProviderStub.usd_table:
            return None
        return Decimal(QuotesProviderStub.usd_table[date])


class TaxableItemQuotatorTest(unittest.TestCase):
    def test_quotation_unsupported_currency_raises_error(self):
        # given
        quotator = BuySellPairPLNQuotator(QuotesProviderStub())
        buy_sell_pair = BuySellPair(
            "PHYS",
            100,
            Money("1000", "SGD"),
            Money("1", "SGD"),
            datetime.date(2000, 12, 26),
            0,
            100,
            Money("1000", "SGD"),
            Money("1", "SGD"),
            datetime.date(2000, 12, 27),
            0,
        )

        # when
        expected_error = capture_exception(quotator.quote, buy_sell_pair)

        # then
        self.assertIsInstance(expected_error, NoQuotesAvailableError)

    def test_quotation_before_available_quotes_raises_error(self):
        # given
        quotator = BuySellPairPLNQuotator(QuotesProviderStub())
        before_available = datetime.date(2000, 12, 20)
        buy_sell_pair = BuySellPair(
            "PHYS",
            100,
            Money("1000", "USD"),
            Money("1", "USD"),
            before_available,
            0,
            100,
            Money("1000", "USD"),
            Money("1", "USD"),
            datetime.date(2000, 12, 27),
            0,
        )

        # when
        expected_error = capture_exception(quotator.quote, buy_sell_pair)

        # then
        self.assertIsInstance(expected_error, NoQuotesAvailableError)

    def test_quotation_after_available_quotes_raises_error(self):
        # given
        quotator = BuySellPairPLNQuotator(QuotesProviderStub())
        after_available = datetime.date(2001, 1, 5)
        buy_sell_pair = BuySellPair(
            "PHYS",
            100,
            Money("1000", "USD"),
            Money("1", "USD"),
            datetime.date(2000, 12, 26),
            0,
            100,
            Money("1000", "USD"),
            Money("1", "USD"),
            after_available,
            0,
        )

        # when
        expected_error = capture_exception(quotator.quote, buy_sell_pair)

        # then
        self.assertIsInstance(expected_error, NoQuotesAvailableError)

    def test_same_amounts_different_quotes(self):
        # given
        quotator = BuySellPairPLNQuotator(QuotesProviderStub())
        buy_sell_pair = BuySellPair(
            "PHYS",
            100,
            Money("1000", "USD"),
            Money("1", "USD"),
            datetime.date(2000, 12, 26),
            0,
            100,
            Money("1000", "USD"),
            Money("1", "USD"),
            datetime.date(2000, 12, 27),
            0,
        )

        # when
        item = quotator.quote(buy_sell_pair)

        # then
        self.assertEqual(item.buy_pln_quotation_date, datetime.date(2000, 12, 23))
        self.assertEqual(item.buy_paid_pln, Decimal(3000))  # 1000 * 3 USD/PLN
        self.assertEqual(item.buy_commission_pln, Decimal(3))  # 1 * 3 USD/PLN

        self.assertEqual(item.sell_pln_quotation_date, datetime.date(2000, 12, 26))
        self.assertEqual(item.sell_received_pln, Decimal(4000))  # 1000 * 4 USD/PLN
        self.assertEqual(item.sell_commission_pln, Decimal(4))  # 1 * 4 USD/PLN

    def test_different_amounts_same_quotes(self):
        # given
        quotator = BuySellPairPLNQuotator(QuotesProviderStub())
        buy_sell_pair = BuySellPair(
            "PHYS",
            100,
            Money("1000", "USD"),
            Money("1", "USD"),
            datetime.date(2000, 12, 21),
            0,
            10,
            Money("100", "USD"),
            Money("2", "USD"),
            datetime.date(2000, 12, 23),
            0,
        )

        # when
        item = quotator.quote(buy_sell_pair)

        # then
        self.assertEqual(item.buy_pln_quotation_date, datetime.date(2000, 12, 20))
        self.assertEqual(item.buy_paid_pln, Decimal(3000))  # 1000 * 3 USD/PLN
        self.assertEqual(item.buy_commission_pln, Decimal(3))  # 1 * 3 USD/PLN

        self.assertEqual(item.sell_pln_quotation_date, datetime.date(2000, 12, 22))
        self.assertEqual(item.sell_received_pln, Decimal(300))  # 100 * 3 USD/PLN
        self.assertEqual(item.sell_commission_pln, Decimal(6))  # 2 * 3 USD/PLN
