import unittest
import datetime
from typing import Optional
from decimal import Decimal
from money import Money

from src.utils.capture_exception import capture_exception
from src.domain.errors import NoQuotesAvailableError
from src.domain.currency import Currency
from src.domain.transactions.dividend_item import DividendItem
from src.domain.quotation.dividend_item_pln_quotator import DividendItemPLNQuotator


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


class DividendItemQuotatorTest(unittest.TestCase):
    def test_quotation_unsupported_currency_raises_error(self):
        # given
        quotator = DividendItemPLNQuotator(QuotesProviderStub())
        dividend = DividendItem(
            received_dividend=Money("100", "SGD"),
            paid_tax=Money("15", "SGD"),
        )

        # when
        expected_error = capture_exception(quotator.quote, dividend)

        # then
        self.assertIsInstance(expected_error, NoQuotesAvailableError)

    def test_quotation_before_available_quotes_raises_error(self):
        # given
        quotator = DividendItemPLNQuotator(QuotesProviderStub())
        before_available = datetime.date(2000, 12, 20)
        dividend = DividendItem(
            received_dividend=Money("100", "USD"),
            paid_tax=Money("15", "USD"),
            date=before_available,
        )

        # when
        expected_error = capture_exception(quotator.quote, dividend)

        # then
        self.assertIsInstance(expected_error, NoQuotesAvailableError)

    def test_quotation_after_available_quotes_raises_error(self):
        # given
        quotator = DividendItemPLNQuotator(QuotesProviderStub())
        after_available = datetime.date(2001, 1, 5)
        quotator = DividendItemPLNQuotator(QuotesProviderStub())
        before_available = datetime.date(2000, 12, 20)
        dividend = DividendItem(
            received_dividend=Money("100", "USD"),
            paid_tax=Money("15", "USD"),
            date=after_available,
        )

        # when
        expected_error = capture_exception(quotator.quote, dividend)

        # then
        self.assertIsInstance(expected_error, NoQuotesAvailableError)

    def test_quote_before_weekend(self):
        # given
        quotator = DividendItemPLNQuotator(QuotesProviderStub())
        dividend = DividendItem(
            received_dividend=Money("100", "USD"),
            paid_tax=Money("15", "USD"),
            date=datetime.date(2000, 12, 24),
        )

        # when
        item = quotator.quote(dividend)

        # then
        self.assertEqual(item.dividend_pln_quotation_date, datetime.date(2000, 12, 23))
        self.assertEqual(item.received_dividend_pln, Decimal(300))  # 100 * 3 USD/PLN
        self.assertEqual(item.paid_tax_pln, Decimal(45))  # 15 * 3 USD/PLN

    def test_quote_after_weekend(self):
        # given
        quotator = DividendItemPLNQuotator(QuotesProviderStub())
        dividend = DividendItem(
            received_dividend=Money("100", "USD"),
            paid_tax=Money("15", "USD"),
            date=datetime.date(2000, 12, 27),
        )

        # when
        item = quotator.quote(dividend)

        # then
        self.assertEqual(item.dividend_pln_quotation_date, datetime.date(2000, 12, 26))
        self.assertEqual(item.received_dividend_pln, Decimal(400))  # 100 * 4 USD/PLN
        self.assertEqual(item.paid_tax_pln, Decimal(60))  # 15 * 4 USD/PLN
