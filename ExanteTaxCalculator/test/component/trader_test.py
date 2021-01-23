import unittest
import datetime
from money import Money
from decimal import Decimal
from typing import Optional
from src.domain.currency import Currency, USD
from src.application.trader import Trader

TAX_PERCENTAGE = Decimal("19.0")


class QuotesProviderStub:
    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        """ Laziness manifestation; always return 1USD = 3PLN """
        if currency != USD:
            raise ValueError(f"Expected USD, got: {currency}")
        return Decimal("3")


class TraderTest(unittest.TestCase):
    def test_empty_input_empty_output(self):
        # given
        csv_report_lines = ['"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"']
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets, {})
        self.assertEqual(trader.profit_items, [])
        self.assertEqual(trader.total_profit, Money("0", "PLN"))
        self.assertEqual(trader.total_tax, Money("0", "PLN"))

    def test_fund_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"EUR"	"1000.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertTrue("EUR" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("1000"))
        self.assertEqual(trader.profit_items, [])
        self.assertEqual(trader.total_profit, Money("0", "PLN"))
        self.assertEqual(trader.total_tax, Money("0", "PLN"))

    def test_fund_exchange_success(self):
        # given
        csv_report_lines = [
            # exchange 1000 EUR -> 1500 USD
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"2001"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"-1000.0"	"EUR"	"-1000.0"	"None"',
            '"2002"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"1500.00"	"USD"	"1000.00"	"None"',
            # add 1000 EUR
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"EUR"	"1000.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertTrue("EUR" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertTrue("USD" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1500"))
        self.assertEqual(trader.profit_items, [])
        self.assertEqual(trader.total_profit, Money("0", "PLN"))
        self.assertEqual(trader.total_tax, Money("0", "PLN"))

    def test_fund_autoconversion_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # exchange 1000 USD -> 2000 SGD
            '"2001"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-10-21 20:40:55"	"2000"	"SGD"	"1.54"	"None"',
            '"2002"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-10-21 20:40:55"	"-1000"	"USD"	"-1.55"	"None"',
            # add 1000 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"USD"	"1000.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["SGD"], Decimal("2000"))
        self.assertEqual(trader.profit_items, [])
        self.assertEqual(trader.total_profit, Money("0", "PLN"))
        self.assertEqual(trader.total_tax, Money("0", "PLN"))

    def test_fund_dividend_without_tax_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # receive dividend
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("100"))
        self.assertEqual(trader.profit_items, [])
        # self.assertEqual(trader.total_profit, Money(100 * 3, "PLN"))  # 1 USD = 3 PLN
        # self.assertEqual(trader.total_tax, Money(19 * 3, "PLN"))  # 1 USD = 3 PLN, tax due = 19%, total tax = 0 included tax + 19 remaining tax

    def test_fund_dividend_with_tax_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # receive dividend, pay tax
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"None"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15"	"USD"	"-12"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("85"))
        self.assertEqual(trader.profit_items, [])
        # self.assertEqual(trader.total_profit, Money(100 * 3, "PLN"))  # 1 USD = 3 PLN
        # self.assertEqual(trader.total_tax, Money(19 * 3, "PLN"))  # 1 USD = 3 PLN, tax due = 19%, total tax = 15 included tax + 4 remaining tax

    def test_fund_tax_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # tax 15 USD
            '"2000"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-10-21 20:40:55"	"-15.0"	"USD"	"-12.0"	"Tax"',
            # add 1000 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"USD"	"1000.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("985"))
        self.assertEqual(trader.profit_items, [])
        self.assertEqual(trader.total_profit, Money("0", "PLN"))
        self.assertEqual(trader.total_tax, Money("0", "PLN"))

    def test_fund_exchange_buy_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # buy 50 PHYS for 700 USD
            '"3001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"3002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"3003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # exchange 1000 EUR -> 1500 USD
            '"2001"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"-1000.0"	"EUR"	"0"	"None"',
            '"2002"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"1500.00"	"USD"	"0"	"None"',
            # add 1000 EUR
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"EUR"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertTrue("EUR" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertTrue("USD" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["USD"], Decimal("800"))
        self.assertTrue("PHYS.ARCA" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("50"))
        self.assertEqual(trader.profit_items, [])
        self.assertEqual(trader.total_profit, Money("0", "PLN"))
        self.assertEqual(trader.total_tax, Money("0", "PLN"))

    def test_fund_exchange_buy_sell_profit_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # sell 50 PHYS for 800 USD
            '"4001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"-50"	"PHYS.ARCA"	"0"	"None"',
            '"4002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"801.0"	"USD"	"0"	"None"',
            '"4003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-23 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # buy 50 PHYS for 700 USD
            '"3001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"3002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"3003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # exchange 1000 EUR -> 1500 USD
            '"2001"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"-1000.0"	"EUR"	"0"	"None"',
            '"2002"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"1500.00"	"USD"	"0"	"None"',
            # add 1000 EUR
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"EUR"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1600"))
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("0"))
        self.assertEqual(trader.profit_items[0].profit, Money("300", "PLN"))  # (801 - 1 - 699 - 1) = 100 USD, USD=3PLN
        self.assertEqual(trader.total_profit, Money("300", "PLN"))
        self.assertEqual(trader.total_tax, Money(300 * TAX_PERCENTAGE / 100, "PLN"))

    def test_fund_exchange_buy_sell_loss_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # sell 50 PHYS for 600 USD
            '"4001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"-50"	"PHYS.ARCA"	"0"	"None"',
            '"4002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"601.0"	"USD"	"0"	"None"',
            '"4003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-23 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # buy 50 PHYS for 700 USD
            '"3001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"3002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"3003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # exchange 1000 EUR -> 1500 USD
            '"2001"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"-1000.0"	"EUR"	"0"	"None"',
            '"2002"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"1500.00"	"USD"	"0"	"None"',
            # add 1000 EUR
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"EUR"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1400"))
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("0"))
        self.assertEqual(trader.profit_items[0].profit, Money("-300", "PLN"))  # (601 - 1 - 699 - 1) = -100 USD; 1USD=3PLN
        self.assertEqual(trader.total_profit, Money("-300", "PLN"))
        self.assertEqual(trader.total_tax, Money(0, "PLN"))

    def test_dividend_tax_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            # collect 100 USD dividend
            '"1001"	"TBA0174.001"	"SHY.ARCA"	"DIVIDEND"	"2020-10-21 20:40:55"	"100"	"USD"	"75"	"Dividend"',
            # pay 15 USD tax
            '"1002"	"TBA0174.001"	"SHY.ARCA"	"TAX"	"2020-10-21 20:40:55"	"-15"	"USD"	"-12"	"Dividend 15% tax"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("85"))
        # self.assertEqual(trader.profit_items[0].profit, Money("-300", "PLN"))  # (601 - 1 - 699 - 1) = -100 USD; 1USD=3PLN
        # self.assertEqual(trader.total_profit, Money("85", "PLN"))
        # self.assertEqual(trader.total_tax, Money(4, "PLN"))  # complement to 19% TAX_PERCENTAGE

    def test_smoke_success(self):
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"62368714"	"TBA0174.001"	"FXF.ARCA"	"TRADE"	"2020-06-29 16:14:54"	"10"	"FXF.ARCA"	"858.3"	"None"',
            '"62368715"	"TBA0174.001"	"FXF.ARCA"	"TRADE"	"2020-06-29 16:14:54"	"-964.4"	"USD"	"-858.3"	"None"',
            '"62368716"	"TBA0174.001"	"FXF.ARCA"	"COMMISSION"	"2020-06-29 16:14:54"	"-0.2"	"USD"	"-0.18"	"None"',
            '"62368586"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:11:46"	"50"	"PHYS.ARCA"	"635.02"	"None"',
            '"62368587"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:11:46"	"-713.5"	"USD"	"-635.02"	"None"',
            '"62368588"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:11:46"	"-1.0"	"USD"	"-0.89"	"None"',
            '"62368459"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"100"	"PHYS.ARCA"	"1269.77"	"None"',
            '"62368460"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"-1426.5"	"USD"	"-1269.77"	"None"',
            '"62368461"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"None"',
            '"62368399"	"TBA0174.001"	"BIL.ARCA"	"TRADE"	"2020-06-29 16:09:51"	"10"	"BIL.ARCA"	"814.77"	"None"',
            '"62368400"	"TBA0174.001"	"BIL.ARCA"	"TRADE"	"2020-06-29 16:09:51"	"-915.4"	"USD"	"-814.77"	"None"',
            '"62368401"	"TBA0174.001"	"BIL.ARCA"	"COMMISSION"	"2020-06-29 16:09:51"	"-0.2"	"USD"	"-0.18"	"None"',
            '"62368182"	"TBA0174.001"	"IEF.ARCA"	"TRADE"	"2020-06-29 16:08:10"	"12"	"IEF.ARCA"	"1303.72"	"None"',
            '"62368183"	"TBA0174.001"	"IEF.ARCA"	"TRADE"	"2020-06-29 16:08:10"	"-1464.6"	"USD"	"-1303.72"	"None"',
            '"62368184"	"TBA0174.001"	"IEF.ARCA"	"COMMISSION"	"2020-06-29 16:08:10"	"-0.24"	"USD"	"-0.21"	"None"',
            '"62368140"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"-70"	"SHY.ARCA"	"-5395.76"	"None"',
            '"62368141"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"6062.0"	"USD"	"5395.76"	"None"',
            '"62368142"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-06-29 16:07:33"	"-1.4"	"USD"	"-1.25"	"None"',
            '"62366548"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-06-29 15:56:45"	"5"	"TLT.NASDAQ"	"733.59"	"None"',
            '"62366552"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-06-29 15:56:45"	"-824.35"	"USD"	"-733.59"	"None"',
            '"62366555"	"TBA0174.001"	"TLT.NASDAQ"	"COMMISSION"	"2020-06-29 15:56:45"	"-0.1"	"USD"	"-0.09"	"None"',
            '"62088984"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-24 19:54:08"	"150"	"SHY.ARCA"	"11534.16"	"None"',
            '"62088986"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-24 19:54:08"	"-12985.5"	"USD"	"-11534.16"	"None"',
            '"62088988"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-06-24 19:54:08"	"-3.0"	"USD"	"-2.66"	"None"',
            '"62088337"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-06-24 19:52:01"	"-13400.0"	"EUR"	"-13400.0"	"None"',
            '"62088340"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-06-24 19:52:01"	"15067.63"	"USD"	"13386.73"	"None"',
            '"61955151"	"TBA0174.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-06-23 14:41:21"	"13400.0"	"EUR"	"13400.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines)

        # then
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1827.24"))
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("150"))
        # self.assertEqual(trader.profit_items[0].profit, Money("-300", "PLN"))  # (601 - 1 - 699 - 1) = -100 USD; 1USD=3PLN
        # self.assertEqual(trader.total_profit, Money("-300", "PLN"))
        self.assertEqual(trader.total_tax, Money(0, "PLN"))