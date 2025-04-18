import unittest
import datetime
from money import Money
from decimal import Decimal
from typing import Optional, Union

from src.domain.currency import Currency
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.profit_item import ProfitPLN
from src.application.trader import Trader

TAX_PERCENTAGE = Decimal("19.0")


def calc_tax(amount: int) -> Decimal:
    return Decimal(amount * TAX_PERCENTAGE / 100)


def USD_TO_PLN(amount: Union[int, Decimal]) -> Money:
    return to_pln("USD", amount)


def SGD_TO_PLN(amount: Union[int, Decimal]) -> Money:
    return to_pln("SGD", amount)


def PLN(amount: Union[int, Decimal]) -> Money:
    return Money(amount, "PLN")


def to_pln(currency: str, amount: Union[int, Decimal]) -> Money:
    quotes_provider = QuotesProviderStub()
    pln_to_currency = quotes_provider.get_average_pln_for_day(Currency(currency), datetime.date(2000, 1, 1))
    assert pln_to_currency is not None
    pln = amount * pln_to_currency
    return PLN(pln)


class QuotesProviderStub:
    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        """Laziness manifestation; always return 1USD = 3PLN, 1SGD = 2PLN"""
        if currency == Currency("USD"):
            return Decimal("3")
        if currency == Currency("SGD"):
            return Decimal("2")

        raise ValueError(f"Expected USD or SGD, got: {currency}")


class TraderTest(unittest.TestCase):
    def test_empty_input_empty_output(self) -> None:
        # given
        csv_report_lines = ['"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"']
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2000)

        # then
        self.assertEqual(trader.owned_asssets, {})
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_fund_withdraw_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # withdraw 50 USD
            '"2000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-21 20:40:55"	"-99"	"USD"	"0"	"None"',
            # add 100 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"100"	"USD"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1"))
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_fund_exchange_success(self) -> None:
        # given
        csv_report_lines = [
            # exchange 1000 EUR -> 1500 USD
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"2001"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"-1000.0"	"EUR"	"-1000.0"	"None"',
            '"2002"	"TBA9999.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-10-21 20:40:55"	"1500.00"	"USD"	"1000.00"	"None"',
            # add 1000 EUR
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"EUR"	"1000.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertTrue("EUR" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertTrue("USD" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1500"))

        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_dividend_together_with_issuance_fee_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"ISIN"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # receive dividend
            '"1001"	"TBA0174.001"	"GSK.NYSE"	"None"	"DIVIDEND"	"2021-10-19 15:12:48"	"100"	"USD"	"6.22"	"14.0 shares 2021-08-19 dividend GSK.NYSE 7.24 USD (0.5175125 per share) dividend fee amount 0.11 USD (0.0075 per share)"	"f6760f1a-a3cc-4f45-b601-89f9dcfe77a9"	"None"',
            # pay fee
            '"1002"	"TBA0174.001"	"GSK.NYSE"	"None"	"ISSUANCE FEE"	"2021-10-19 15:12:48"	"-15"	"USD"	"-0.09"	"None"	"d7737eff-a58b-4fa2-a81d-c56facbf7c53"	"f6760f1a-a3cc-4f45-b601-89f9dcfe77a9"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2021)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("85"))  # dividend minus issuance fee
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, USD_TO_PLN(100))
        self.assertEqual(trader.report.results.dividends_total_tax, USD_TO_PLN(calc_tax(100)))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, USD_TO_PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, USD_TO_PLN(calc_tax(100)))
        self.assertEqual(trader.report.trades_by_asset, {})

        self.assertEqual(len(trader.report.dividends), 1)
        dividend = trader.report.dividends[0]
        self.assertIsInstance(dividend, DividendItemPLN)
        self.assertEqual(trader.report.dividend_taxes, [])
        self.assertEqual(dividend.received_dividend_pln, USD_TO_PLN(100).amount)
        self.assertEqual(dividend.dividend_pln_quotation_date, datetime.date(2021, 10, 18))

    def test_dividend_without_tax_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # receive dividend
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("100"))
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, USD_TO_PLN(100))
        self.assertEqual(trader.report.results.dividends_total_tax, USD_TO_PLN(calc_tax(100)))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, USD_TO_PLN(calc_tax(100)))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividend_taxes, [])
        item = trader.report.dividends[0]
        self.assertIsInstance(item, DividendItemPLN)
        self.assertEqual(item.received_dividend_pln, Decimal(300))
        self.assertEqual(item.dividend_pln_quotation_date, datetime.date(2020, 6, 23))
        self.assertIsNone(item.paid_tax_pln)
        self.assertIsNone(item.paid_tax_pln)

    def test_dividend_together_with_tax_success(self) -> None:
        """Here dividend item contains tax"""

        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # collect 100 USD dividend
            '"1001"	"TBA0174.001"	"SHY.ARCA"	"DIVIDEND"	"2020-10-20 20:40:55"	"100"	"USD"	"75"	"Dividend"',
            # pay 15 USD tax
            '"1002"	"TBA0174.001"	"SHY.ARCA"	"TAX"	"2020-10-20 20:40:55"	"-15"	"USD"	"-12"	"Dividend 15% tax"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("85"))
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, USD_TO_PLN(100))
        self.assertEqual(trader.report.results.dividends_total_tax, USD_TO_PLN(calc_tax(100)))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, USD_TO_PLN(15))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, USD_TO_PLN(calc_tax(100) - 15))
        self.assertEqual(trader.report.trades_by_asset, {})

        dividend = trader.report.dividends[0]
        tax = trader.report.dividend_taxes[0]
        assert isinstance(dividend, DividendItemPLN)
        assert isinstance(tax, TaxItemPLN)
        self.assertEqual(dividend.received_dividend_pln, USD_TO_PLN(100).amount)
        self.assertEqual(dividend.dividend_pln_quotation_date, datetime.date(2020, 10, 19))
        self.assertEqual(tax.paid_tax_pln, USD_TO_PLN(15).amount)
        self.assertEqual(tax.tax_pln_quotation_date, datetime.date(2020, 10, 19))

    def test_dividend_separate_from_tax_success(self) -> None:
        """Here dividend is separate item from tax item"""

        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # then pay 15 USD tax
            '"2001"	"TBA0174.001"	"TLT"	"TAX"	"2020-10-21 20:40:55"	"-15"	"USD"	"-12"	"Dividend 15% tax"',
            # first collect 100 USD dividend
            '"1001"	"TBA0174.001"	"SHY.ARCA"	"DIVIDEND"	"2020-10-20 20:40:55"	"100"	"USD"	"75"	"Dividend"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("85"))
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, USD_TO_PLN(100))
        self.assertEqual(trader.report.results.dividends_total_tax, USD_TO_PLN(calc_tax(100)))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, USD_TO_PLN(15))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, USD_TO_PLN(calc_tax(100) - 15))
        self.assertEqual(trader.report.trades_by_asset, {})

        dividend = trader.report.dividends[0]
        tax = trader.report.dividend_taxes[0]
        assert isinstance(dividend, DividendItemPLN)
        assert isinstance(tax, TaxItemPLN)
        self.assertEqual(dividend.received_dividend_pln, USD_TO_PLN(100).amount)
        self.assertEqual(dividend.dividend_pln_quotation_date, datetime.date(2020, 10, 19))
        self.assertEqual(tax.paid_tax_pln, USD_TO_PLN(15).amount)
        self.assertEqual(tax.tax_pln_quotation_date, datetime.date(2020, 10, 20))

    def test_fund_tax_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # tax 15 USD
            '"2000"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-10-21 20:40:55"	"-15.0"	"USD"	"-12.0"	"Tax"',
            # add 1000 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"USD"	"1000.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("985"))
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))  # no profit at all
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))  # no profit = no tax to pay
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, USD_TO_PLN(15))  # but they deducted some tax anyway... life.
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        tax = trader.report.dividend_taxes[0]

        assert isinstance(tax, TaxItemPLN)
        self.assertEqual(tax.paid_tax_pln, USD_TO_PLN(15).amount)
        self.assertEqual(tax.tax_pln_quotation_date, datetime.date(2020, 10, 20))

    def test_fund_issuance_fee_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # issuance fee 15 USD
            '"2000"	"TBA0174.001"	"TLT.NASDAQ"	"ISSUANCE FEE"	"2020-10-21 20:40:55"	"-15.0"	"USD"	"-12.0"	"Issuance fee"',
            # add 1000 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1000.0"	"USD"	"1000.0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("985"))  # 1000 minus issuance fee
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))  # no profit at all
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))  # no profit = no tax to pay
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_fund_exchange_buy_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
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
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertTrue("EUR" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertTrue("USD" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["USD"], Decimal("800"))
        self.assertTrue("PHYS.ARCA" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("50"))

        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))  # cost is only generated from buy/sell pair
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_fund_buy_with_autoconversion_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # buy 50 PHYS for 700 USD with autoconversion from EUR
            '"3001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"3002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"3003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            '"3004"	"TBA9999.001"	"PHYS.ARCA"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"699"	"USD"	"499.5"	"None"',
            '"3005"	"TBA9999.001"	"PHYS.ARCA"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"-499.5"	"EUR"	"-499.5"	"None"',
            '"3006"	"TBA9999.001"	"PHYS.ARCA"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"1"	"USD"	"0.5"	"None"',
            '"3007"	"TBA9999.001"	"PHYS.ARCA"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"-0.5"	"EUR"	"-0.5"	"None"',
            # add 500 EUR
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"500.0"	"EUR"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertTrue("EUR" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertTrue("USD" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["USD"], Decimal("0"))
        self.assertTrue("PHYS.ARCA" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("50"))

        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))  # cost is only generated from buy/sell pair
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_fund_buy_with_autoconversion_sell_with_autoconversion_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # sell 50 CLR.SGX for 1500 SGD with autoconversion to 1200 USD including commission
            '"4001"	"TBA9999.001"	"CLR.SGX"	"TRADE"	"2020-10-23 20:40:55"	"-50"	"CLR.SGX"	"0"	"None"',
            '"4002"	"TBA9999.001"	"CLR.SGX"	"TRADE"	"2020-10-23 20:40:55"	"1502"	"SGD"	"0"	"None"',
            '"4003"	"TBA9999.001"	"CLR.SGX"	"COMMISSION"	"2020-10-23 20:40:55"	"-2"	"SGD"	"0"	"None"',
            '"4004"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2021-02-09 07:46:39"	"-1502"	"SGD"	"0"	"None"',
            '"4005"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2021-02-09 07:46:39"	"1201"	"USD"	"0"	"None"',
            '"4006"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2021-02-09 07:46:39"	"2"	"SGD"	"0"	"None"',
            '"4007"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2021-02-09 07:46:39"	"-1"	"USD"	"0"	"None"',
            # buy 50 CLR.SGX for 1000 SGD  with autoconversion from 800 USD including commission
            '"3001"	"TBA9999.001"	"CLR.SGX"	"TRADE"	"2020-10-22 20:40:55"	"50"	"CLR.SGX"	"0"	"None"',
            '"3002"	"TBA9999.001"	"CLR.SGX"	"TRADE"	"2020-10-22 20:40:55"	"-998"	"SGD"	"0"	"None"',
            '"3003"	"TBA9999.001"	"CLR.SGX"	"COMMISSION"	"2020-10-22 20:40:55"	"-2.0"	"SGD"	"0"	"None"',
            '"3004"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"998"	"SGD"	"0"	"None"',
            '"3005"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"-799"	"USD"	"0"	"None"',
            '"3006"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"2"	"SGD"	"0"	"None"',
            '"3007"	"TBA9999.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-10-22 20:40:55"	"-1"	"USD"	"0"	"None"',
            # add 800 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"800.0"	"USD"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1200"))
        self.assertEqual(trader.owned_asssets["SGD"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["CLR.SGX"], Decimal("0"))
        self.assertEqual(trader.report.results.shares_total_income, SGD_TO_PLN(1500))
        self.assertEqual(trader.report.results.shares_total_cost, SGD_TO_PLN(1000))
        self.assertEqual(trader.report.results.shares_total_tax, SGD_TO_PLN(calc_tax(500)))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

        profit = trader.report.trades_by_asset["CLR.SGX"][0]
        assert isinstance(profit, ProfitPLN)
        self.assertEqual(profit.paid, SGD_TO_PLN(1000))
        self.assertEqual(profit.received, SGD_TO_PLN(1500))

    def test_dividend_with_autoconversion_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"DIVIDEND"	"2020-12-08 06:27:21"	"30"	"SGD"	"0"	"1300.0 shares (0.024 per share)"',
            '"2"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-30.0"	"SGD"	"0"	"1300.0 shares (0.024 per share)"',
            '"3"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"20.0"	"USD"	"0"	"1300.0  (0.024 per share)"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertTrue("SGD" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["SGD"], Decimal("0"))
        self.assertTrue("USD" in trader.owned_asssets)
        self.assertEqual(trader.owned_asssets["USD"], Decimal("20.0"))

        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, SGD_TO_PLN(30))
        self.assertEqual(trader.report.results.dividends_total_tax, SGD_TO_PLN(calc_tax(30)))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, SGD_TO_PLN(calc_tax(30)))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividend_taxes, [])

        dividend = trader.report.dividends[0]
        assert isinstance(dividend, DividendItemPLN)
        self.assertEqual(dividend.received_dividend_pln, SGD_TO_PLN(30).amount)
        self.assertEqual(dividend.dividend_pln_quotation_date, datetime.date(2020, 12, 7))
        self.assertIsNone(dividend.paid_tax_pln)

    def test_fund_exchange_buy_sell_profit_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
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
        trader.trade_items(csv_report_lines, 2020)

        # then
        total_tax = 100 * (TAX_PERCENTAGE / 100)
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1600"))
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("0"))
        self.assertEqual(trader.report.results.shares_total_income, USD_TO_PLN(800))
        self.assertEqual(trader.report.results.shares_total_cost, USD_TO_PLN(700))
        self.assertEqual(trader.report.results.shares_total_tax, USD_TO_PLN(total_tax))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

        profit = trader.report.trades_by_asset["PHYS.ARCA"][0]
        assert isinstance(profit, ProfitPLN)
        self.assertEqual(profit.paid, USD_TO_PLN(700))
        self.assertEqual(profit.received, USD_TO_PLN(800))

    def test_fund_exchange_buy_sell_loss_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
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
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["EUR"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1400"))
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("0"))
        self.assertEqual(trader.report.results.shares_total_income, USD_TO_PLN(600))
        self.assertEqual(trader.report.results.shares_total_cost, USD_TO_PLN(700))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

        profit = trader.report.trades_by_asset["PHYS.ARCA"][0]
        assert isinstance(profit, ProfitPLN)
        self.assertEqual(profit.paid, USD_TO_PLN(700))
        self.assertEqual(profit.received, USD_TO_PLN(600))

    def test_fund_buy_corporate_action_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # corporate action 10 SHY.ARCA -> 10 SHY.NYSE
            '"3001"	"TBA9999.001"	"SHY.ARCA"	"CORPORATE ACTION"	"2020-10-22 20:40:55"	"-10"	"SHY.ARCA"	"-2027.87"	"SHY.ARCA to SHY.NYSE"',
            '"3002"	"TBA9999.001"	"SHY.NYSE"	"CORPORATE ACTION"	"2020-10-22 20:40:55"	"10"	"SHY.NYSE"	"2063.21"	"SHY.ARCA to SHY.NYSE"',
            # buy 10 SHY.ARCA
            '"2001"	"TBA9999.001"	"SHY.ARCA"	"TRADE"	"2020-10-21 20:40:55"	"10"	"SHY.ARCA"	"0"	"None"',
            '"2002"	"TBA9999.001"	"SHY.ARCA"	"TRADE"	"2020-10-21 20:40:55"	"-99.0"	"USD"	"0"	"None"',
            '"2003"	"TBA9999.001"	"SHY.ARCA"	"COMMISSION"	"2020-10-21 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # add 100 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"100"	"USD"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["SHY.ARCA"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["SHY.NYSE"], Decimal("10"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("0"))
        self.assertEqual(trader.report.results.shares_total_income, PLN(0))
        self.assertEqual(trader.report.results.shares_total_cost, PLN(0))
        self.assertEqual(trader.report.results.shares_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))
        self.assertEqual(trader.report.trades_by_asset, {})
        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_fund_buy_stock_split_sell_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # sell 200 2768.TSE (all of them)
            '"4001"	"TBA9999.001"	"2768.TSE"	"TRADE"	"2021-09-30 06:56:01"	"101"	"USD"	"0"	"None"',
            '"4002"	"TBA9999.001"	"2768.TSE"	"TRADE"	"2021-09-30 06:56:01"	"-200"	"2768.TSE"	"0"	"None"',
            '"4003"	"TBA9999.001"	"2768.TSE"	"COMMISSION"	"2021-09-30 06:56:01"	"-1.0"	"USD"	"0"	"None"',
            # stock split 100 2768.TSE -> 200 2768.TSE
            '"3001"	"TBA9999.001"	"2768.TSE"	"STOCK SPLIT"	"2021-09-29 06:56:01"	"200"	"2768.TSE"	"241"	"2768.TSE split 2 for 1"',
            '"3002"	"TBA9999.001"	"2768.TSE"	"STOCK SPLIT"	"2021-09-29 06:56:01"	"-100"	"2768.TSE"	"-241"	"2768.TSE split 2 for 1"',
            # buy 100 2768.TSE
            '"2001"	"TBA9999.001"	"2768.TSE"	"TRADE"	"2021-09-28 06:56:01"	"100"	"2768.TSE"	"0"	"None"',
            '"2002"	"TBA9999.001"	"2768.TSE"	"TRADE"	"2021-09-28 06:56:01"	"-99.0"	"USD"	"0"	"None"',
            '"2003"	"TBA9999.001"	"2768.TSE"	"COMMISSION"	"2021-09-28 06:56:01"	"-1.0"	"USD"	"0"	"None"',
            # add 100 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2021-09-27 06:56:01"	"100"	"USD"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2021)

        # then
        self.assertEqual(trader.owned_asssets["2768.TSE"], Decimal("0"))  # after buy 100 and split to 200, all 200 sold
        self.assertEqual(trader.owned_asssets["USD"], Decimal(101 - 1))  # 101 from selling minus 1 commission
        self.assertEqual(trader.report.results.shares_total_income, USD_TO_PLN(101 - 1))
        self.assertEqual(trader.report.results.shares_total_cost, USD_TO_PLN(100))
        self.assertEqual(trader.report.results.shares_total_tax, USD_TO_PLN(calc_tax(0)))  # income-cost; no profit this time
        self.assertEqual(trader.report.results.dividends_total_income, PLN(0))
        self.assertEqual(trader.report.results.dividends_total_tax, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, PLN(0))

        profit = trader.report.trades_by_asset["2768.TSE"][0]
        assert isinstance(profit, ProfitPLN)
        self.assertEqual(profit.paid, USD_TO_PLN(100))
        self.assertEqual(profit.received, USD_TO_PLN(101 - 1))

        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_two_years_report_calc_for_first_year(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # year 2021: we lose 100 USD
            # sell 50 PHYS for 600 USD
            '"6001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-23 20:40:55"	"-50"	"PHYS.ARCA"	"0"	"None"',
            '"6002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-23 20:40:55"	"601.0"	"USD"	"0"	"None"',
            '"6003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2021-10-23 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # buy 50 PHYS for 700 USD
            '"5001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"5002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"5003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2021-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # year 2020: we profit 100 USD
            # sell 50 PHYS for 800 USD
            '"4001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"-50"	"PHYS.ARCA"	"0"	"None"',
            '"4002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"801.0"	"USD"	"0"	"None"',
            '"4003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-23 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # buy 50 PHYS for 700 USD
            '"3001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"3002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"3003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # add 1500 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1500.0"	"USD"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2020)

        # then
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1500"))
        self.assertEqual(trader.report.results.shares_total_income, USD_TO_PLN(800))
        self.assertEqual(trader.report.results.shares_total_cost, USD_TO_PLN(700))
        self.assertEqual(trader.report.results.shares_total_tax, USD_TO_PLN(calc_tax(100)))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, USD_TO_PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, USD_TO_PLN(0))

        profit = trader.report.trades_by_asset["PHYS.ARCA"][0]
        assert isinstance(profit, ProfitPLN)
        self.assertEqual(profit.paid, USD_TO_PLN(700))
        self.assertEqual(profit.received, USD_TO_PLN(800))

        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_two_years_report_calc_for_second_year(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            # year 2021: we lose 100 USD
            # sell 50 PHYS for 600 USD
            '"6001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-23 20:40:55"	"-50"	"PHYS.ARCA"	"0"	"None"',
            '"6002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-23 20:40:55"	"601.0"	"USD"	"0"	"None"',
            '"6003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2021-10-23 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # buy 50 PHYS for 700 USD
            '"5001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"5002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2021-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"5003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2021-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # year 2020: we profit 100 USD
            # sell 50 PHYS for 800 USD
            '"4001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"-50"	"PHYS.ARCA"	"0"	"None"',
            '"4002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-23 20:40:55"	"801.0"	"USD"	"0"	"None"',
            '"4003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-23 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # buy 50 PHYS for 700 USD
            '"3001"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"50"	"PHYS.ARCA"	"0"	"None"',
            '"3002"	"TBA9999.001"	"PHYS.ARCA"	"TRADE"	"2020-10-22 20:40:55"	"-699.0"	"USD"	"0"	"None"',
            '"3003"	"TBA9999.001"	"PHYS.ARCA"	"COMMISSION"	"2020-10-22 20:40:55"	"-1.0"	"USD"	"0"	"None"',
            # add 1500 USD
            '"1000"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 20:40:55"	"1500.0"	"USD"	"0"	"None"',
        ]
        quotes_provider_stub = QuotesProviderStub()
        trader = Trader(quotes_provider=quotes_provider_stub, tax_percentage=TAX_PERCENTAGE)

        # when
        trader.trade_items(csv_report_lines, 2021)

        # then
        self.assertEqual(trader.owned_asssets["PHYS.ARCA"], Decimal("0"))
        self.assertEqual(trader.owned_asssets["USD"], Decimal("1500"))
        self.assertEqual(trader.report.results.shares_total_income, USD_TO_PLN(600))
        self.assertEqual(trader.report.results.shares_total_cost, USD_TO_PLN(700))
        self.assertEqual(trader.report.results.shares_total_tax, USD_TO_PLN(calc_tax(0)))
        self.assertEqual(trader.report.results.dividends_tax_already_paid, USD_TO_PLN(0))
        self.assertEqual(trader.report.results.dividends_tax_yet_to_be_paid, USD_TO_PLN(0))

        profit = trader.report.trades_by_asset["PHYS.ARCA"][0]
        assert isinstance(profit, ProfitPLN)
        self.assertEqual(profit.paid, USD_TO_PLN(700))
        self.assertEqual(profit.received, USD_TO_PLN(600))

        self.assertEqual(trader.report.dividends, [])
        self.assertEqual(trader.report.dividend_taxes, [])

    def test_smoke_success(self) -> None:
        # given
        csv_report_lines = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"97505780"	"TBA0174.001"	"GSK.NYSE"	"ISSUANCE FEE"	"2021-04-14 08:44:35"	"-15.0"	"USD"	"-12.0"	"Issuance Fee"',
            '"79327161"	"TBA0174.001"	"OGZD.LSEIOB"	"TRADE"	"2020-12-22 09:05:44"	"-125"	"OGZD.LSEIOB"	"-559.66"	"None"',
            '"79327162"	"TBA0174.001"	"OGZD.LSEIOB"	"TRADE"	"2020-12-22 09:05:44"	"684.0"	"USD"	"559.66"	"None"',
            '"79327163"	"TBA0174.001"	"OGZD.LSEIOB"	"COMMISSION"	"2020-12-22 09:05:44"	"-0.35"	"USD"	"-0.29"	"None"',
            '"79160832"	"TBA0174.001"	"GDXJ.ARCA"	"DIVIDEND"	"2020-12-21 11:31:04"	"8.55"	"USD"	"7.03"	"10.0 shares 2020-12-21 dividend GDXJ.ARCA 8.55 USD (0.8554 per share) tax 1.29 USD (15.0%)"',
            '"79160833"	"TBA0174.001"	"GDXJ.ARCA"	"TAX"	"2020-12-21 11:31:04"	"-1.29"	"USD"	"-1.06"	"None"',
            '"78758900"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-12-17 11:02:26"	"10.66"	"USD"	"8.72"	"65.0 shares 2020-12-17 dividend TLT.NASDAQ 10.66 USD (0.163928 per share) tax 1.6 USD (15.0%)"',
            '"78758901"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-12-17 11:02:26"	"-1.6"	"USD"	"-1.31"	"None"',
            '"78757917"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-12-17 11:02:25"	"1.45"	"USD"	"1.19"	"20.0 shares 2020-12-17 dividend IEF.NASDAQ 1.45 USD (0.072535 per share) tax 0.22 USD (15.0%)"',
            '"78757918"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-12-17 11:02:25"	"-0.22"	"USD"	"-0.18"	"None"',
            '"77471449"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"1300"	"CLR.SGX"	"857.24"	"None"',
            '"77471450"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"-1388.4"	"SGD"	"-857.24"	"None"',
            '"77471451"	"TBA0174.001"	"CLR.SGX"	"COMMISSION"	"2020-12-08 06:27:21"	"-2.5"	"SGD"	"-1.54"	"None"',
            '"77471452"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"1388.4"	"SGD"	"857.24"	"None"',
            '"77471453"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1040.98"	"USD"	"-858.95"	"None"',
            '"77471454"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"2.5"	"SGD"	"1.54"	"None"',
            '"77471455"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1.88"	"USD"	"-1.55"	"None"',
            '"77424034"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-12-07 17:27:08"	"-8"	"TLT.NASDAQ"	"-1031.69"	"None"',
            '"77424035"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-12-07 17:27:08"	"1252.24"	"USD"	"1031.69"	"None"',
            '"77424036"	"TBA0174.001"	"TLT.NASDAQ"	"COMMISSION"	"2020-12-07 17:27:08"	"-0.16"	"USD"	"-0.13"	"None"',
            '"76663645"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-12-01 11:02:09"	"11.9"	"USD"	"9.94"	"73.0 shares 2020-12-01 dividend TLT.NASDAQ 11.9 USD (0.163003 per share) tax 1.79 USD (15.0%)"',
            '"76663646"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-12-01 11:02:09"	"-1.79"	"USD"	"-1.5"	"None"',
            '"76662764"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-12-01 11:02:08"	"1.6"	"USD"	"1.34"	"20.0 shares 2020-12-01 dividend IEF.NASDAQ 1.6 USD (0.079751 per share) tax 0.24 USD (15.0%)"',
            '"76662765"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-12-01 11:02:08"	"-0.24"	"USD"	"-0.2"	"None"',
            '"73469732"	"TBA0174.001"	"OGZD.LSEIOB"	"TRADE"	"2020-11-04 15:31:38"	"130"	"OGZD.LSEIOB"	"455.95"	"None"',
            '"73469733"	"TBA0174.001"	"OGZD.LSEIOB"	"TRADE"	"2020-11-04 15:31:38"	"-534.17"	"USD"	"-455.95"	"None"',
            '"73469734"	"TBA0174.001"	"OGZD.LSEIOB"	"COMMISSION"	"2020-11-04 15:31:38"	"-0.27"	"USD"	"-0.23"	"None"',
            '"73469607"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-11-04 15:30:55"	"-20"	"UUP.ARCA"	"-430.66"	"None"',
            '"73469608"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-11-04 15:30:55"	"504.4"	"USD"	"430.66"	"None"',
            '"73469609"	"TBA0174.001"	"UUP.ARCA"	"COMMISSION"	"2020-11-04 15:30:55"	"-0.4"	"USD"	"-0.34"	"None"',
            '"73181405"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-11-02 11:01:45"	"12.37"	"USD"	"10.62"	"73.0 shares 2020-11-02 dividend TLT.NASDAQ 12.37 USD (0.169451 per share) tax 1.86 USD (15.0%)"',
            '"73181406"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-11-02 11:01:45"	"-1.86"	"USD"	"-1.6"	"None"',
            '"73180634"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-11-02 11:01:45"	"1.52"	"USD"	"1.31"	"20.0 shares 2020-11-02 dividend IEF.NASDAQ 1.52 USD (0.075943 per share) tax 0.23 USD (15.0%)"',
            '"73180637"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-11-02 11:01:45"	"-0.23"	"USD"	"-0.2"	"None"',
            '"72637626"	"TBA0174.001"	"IEF.ARCA"	"CORPORATE ACTION"	"2020-10-27 16:36:04"	"-20"	"IEF.ARCA"	"-2027.87"	"IEF.ARCA to IEF.NASDAQ"',
            '"72637631"	"TBA0174.001"	"IEF.NASDAQ"	"CORPORATE ACTION"	"2020-10-27 16:36:04"	"20"	"IEF.NASDAQ"	"2063.21"	"IEF.ARCA to IEF.NASDAQ"',
            '"71411855"	"TBA0174.001"	"OGZD.LSEIOB"	"TRADE"	"2020-10-14 13:45:37"	"120"	"OGZD.LSEIOB"	"436.27"	"None"',
            '"71411856"	"TBA0174.001"	"OGZD.LSEIOB"	"TRADE"	"2020-10-14 13:45:37"	"-513.12"	"USD"	"-436.27"	"None"',
            '"71411857"	"TBA0174.001"	"OGZD.LSEIOB"	"COMMISSION"	"2020-10-14 13:45:37"	"-0.26"	"USD"	"-0.22"	"None"',
            '"71411619"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-10-14 13:45:00"	"-2"	"TLT.NASDAQ"	"-275.61"	"None"',
            '"71411620"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-10-14 13:45:00"	"324.16"	"USD"	"275.61"	"None"',
            '"71411621"	"TBA0174.001"	"TLT.NASDAQ"	"COMMISSION"	"2020-10-14 13:45:00"	"-0.04"	"USD"	"-0.03"	"None"',
            '"70340332"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-10-01 11:03:01"	"12.68"	"USD"	"10.8"	"75.0 shares 2020-10-01 dividend TLT.NASDAQ 12.68 USD (0.16906 per share) tax 1.91 USD (15.0%)"',
            '"70340333"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-10-01 11:03:01"	"-1.91"	"USD"	"-1.63"	"None"',
            '"70339735"	"TBA0174.001"	"IEF.ARCA"	"DIVIDEND"	"2020-10-01 11:03:00"	"1.59"	"USD"	"1.35"	"20.0 shares 2020-10-01 dividend IEF.ARCA 1.59 USD (0.079256 per share) tax 0.24 USD (15.0%)"',
            '"70339736"	"TBA0174.001"	"IEF.ARCA"	"TAX"	"2020-10-01 11:03:00"	"-0.24"	"USD"	"-0.2"	"None"',
            '"70028502"	"TBA0174.001"	"PSLV.ARCA"	"TRADE"	"2020-09-28 13:53:55"	"90"	"PSLV.ARCA"	"638.04"	"None"',
            '"70028507"	"TBA0174.001"	"PSLV.ARCA"	"TRADE"	"2020-09-28 13:53:55"	"-744.3"	"USD"	"-638.04"	"None"',
            '"70028511"	"TBA0174.001"	"PSLV.ARCA"	"COMMISSION"	"2020-09-28 13:53:55"	"-1.8"	"USD"	"-1.54"	"None"',
            '"68428951"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-09-08 17:53:16"	"65"	"TLT.NASDAQ"	"9044.44"	"None"',
            '"68428952"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-09-08 17:53:16"	"-10665.2"	"USD"	"-9044.44"	"None"',
            '"68428953"	"TBA0174.001"	"TLT.NASDAQ"	"COMMISSION"	"2020-09-08 17:53:16"	"-1.3"	"USD"	"-1.1"	"None"',
            '"68428845"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-09-08 17:51:58"	"-100"	"SHY.ARCA"	"-7332.56"	"None"',
            '"68428846"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-09-08 17:51:58"	"8647.0"	"USD"	"7332.56"	"None"',
            '"68428847"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-09-08 17:51:58"	"-2.0"	"USD"	"-1.7"	"None"',
            '"68428835"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-09-08 17:51:58"	"-35"	"SHY.ARCA"	"-2566.4"	"None"',
            '"68428836"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-09-08 17:51:58"	"3026.45"	"USD"	"2566.4"	"None"',
            '"68428837"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-09-08 17:51:58"	"-0.7"	"USD"	"-0.59"	"None"',
            '"68270844"	"TBA0174.001"	"SHY.ARCA"	"DIVIDEND"	"2020-09-07 17:10:22"	"6.63"	"USD"	"5.61"	"135.0 shares 2020-09-01 dividend SHY.ARCA 6.63 USD (0.049132 per share) tax 1.0 USD (15.0%)"',
            '"68270845"	"TBA0174.001"	"SHY.ARCA"	"TAX"	"2020-09-07 17:10:22"	"-1.0"	"USD"	"-0.85"	"None"',
            '"68270363"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-09-07 17:09:15"	"1.83"	"USD"	"1.55"	"10.0 shares 2020-09-01 dividend TLT.NASDAQ 1.83 USD (0.18292 per share) tax 0.28 USD (15.0%)"',
            '"68270364"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-09-07 17:09:15"	"-0.28"	"USD"	"-0.24"	"None"',
            '"68269992"	"TBA0174.001"	"IEF.ARCA"	"DIVIDEND"	"2020-09-07 17:08:43"	"1.76"	"USD"	"1.49"	"20.0 shares 2020-09-01 dividend IEF.ARCA 1.76 USD (0.088008 per share) tax 0.27 USD (15.0%)"',
            '"68269993"	"TBA0174.001"	"IEF.ARCA"	"TAX"	"2020-09-07 17:08:43"	"-0.27"	"USD"	"-0.23"	"None"',
            '"66935452"	"TBA0174.001"	"GDXJ.ARCA"	"TRADE"	"2020-08-24 15:50:46"	"10"	"GDXJ.ARCA"	"487.34"	"None"',
            '"66935453"	"TBA0174.001"	"GDXJ.ARCA"	"TRADE"	"2020-08-24 15:50:46"	"-575.1"	"USD"	"-487.34"	"None"',
            '"66935454"	"TBA0174.001"	"GDXJ.ARCA"	"COMMISSION"	"2020-08-24 15:50:46"	"-0.2"	"USD"	"-0.17"	"None"',
            '"66914011"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-08-24 14:08:32"	"25"	"SHY.ARCA"	"1828.83"	"None"',
            '"66914012"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-08-24 14:08:32"	"-2163.0"	"USD"	"-1828.83"	"None"',
            '"66914013"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-08-24 14:08:32"	"-0.5"	"USD"	"-0.42"	"None"',
            '"66900593"	"TBA0174.001"	"FXF.ARCA"	"TRADE"	"2020-08-24 13:30:07"	"-20"	"FXF.ARCA"	"-1700.27"	"None"',
            '"66900594"	"TBA0174.001"	"FXF.ARCA"	"TRADE"	"2020-08-24 13:30:07"	"2012.8"	"USD"	"1700.27"	"None"',
            '"66900595"	"TBA0174.001"	"FXF.ARCA"	"COMMISSION"	"2020-08-24 13:30:07"	"-0.4"	"USD"	"-0.34"	"None"',
            '"65568632"	"TBA0174.001"	"SHY.ARCA"	"DIVIDEND"	"2020-08-06 11:14:08"	"5.55"	"USD"	"4.69"	"110.0 shares 2020-08-03 dividend SHY.ARCA 5.55 USD (0.050443 per share) tax 0.84 USD (15.0%)"',
            '"65568633"	"TBA0174.001"	"SHY.ARCA"	"TAX"	"2020-08-06 11:14:08"	"-0.84"	"USD"	"-0.71"	"None"',
            '"65567833"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-08-06 11:11:25"	"1.9"	"USD"	"1.61"	"10.0 shares 2020-08-03 dividend TLT.NASDAQ 1.9 USD (0.19014 per share) tax 0.29 USD (15.0%)"',
            '"65567834"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-08-06 11:11:25"	"-0.29"	"USD"	"-0.24"	"None"',
            '"65308131"	"TBA0174.001"	"IEF.ARCA"	"DIVIDEND"	"2020-08-04 10:33:28"	"2.0"	"USD"	"1.7"	"20.0 shares 2020-08-03 dividend IEF.ARCA 2.0 USD (0.099876 per share) tax 0.3 USD (15.0%)"',
            '"65308132"	"TBA0174.001"	"IEF.ARCA"	"TAX"	"2020-08-04 10:33:28"	"-0.3"	"USD"	"-0.25"	"None"',
            '"64659042"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-07-27 15:49:47"	"100"	"UUP.ARCA"	"2152.23"	"None"',
            '"64659043"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-07-27 15:49:47"	"-2530.0"	"USD"	"-2152.23"	"None"',
            '"64659044"	"TBA0174.001"	"UUP.ARCA"	"COMMISSION"	"2020-07-27 15:49:47"	"-2.0"	"USD"	"-1.7"	"None"',
            '"64659033"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-07-27 15:49:47"	"90"	"UUP.ARCA"	"1937.01"	"None"',
            '"64659034"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-07-27 15:49:47"	"-2277.0"	"USD"	"-1937.01"	"None"',
            '"64659035"	"TBA0174.001"	"UUP.ARCA"	"COMMISSION"	"2020-07-27 15:49:47"	"-1.8"	"USD"	"-1.53"	"None"',
            '"64659024"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-07-27 15:49:47"	"10"	"UUP.ARCA"	"215.22"	"None"',
            '"64659025"	"TBA0174.001"	"UUP.ARCA"	"TRADE"	"2020-07-27 15:49:47"	"-253.0"	"USD"	"-215.22"	"None"',
            '"64659026"	"TBA0174.001"	"UUP.ARCA"	"COMMISSION"	"2020-07-27 15:49:47"	"-0.2"	"USD"	"-0.17"	"None"',
            '"64627600"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-07-27 13:30:07"	"-40"	"SHY.ARCA"	"-2950.59"	"None"',
            '"64627605"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-07-27 13:30:07"	"3462.4"	"USD"	"2950.59"	"None"',
            '"64627609"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-07-27 13:30:07"	"-0.8"	"USD"	"-0.68"	"None"',
            '"64497509"	"TBA0174.001"	"BIL.ARCA"	"TRADE"	"2020-07-24 13:30:12"	"-20"	"BIL.ARCA"	"-1576.38"	"None"',
            '"64497510"	"TBA0174.001"	"BIL.ARCA"	"TRADE"	"2020-07-24 13:30:12"	"1830.6"	"USD"	"1576.38"	"None"',
            '"64497512"	"TBA0174.001"	"BIL.ARCA"	"COMMISSION"	"2020-07-24 13:30:12"	"-0.4"	"USD"	"-0.34"	"None"',
            '"64407719"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-07-23 16:16:31"	"70"	"SHY.ARCA"	"5216.74"	"None"',
            '"64407720"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-07-23 16:16:31"	"-6059.9"	"USD"	"-5216.74"	"None"',
            '"64407721"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-07-23 16:16:31"	"-1.4"	"USD"	"-1.21"	"None"',
            '"64407586"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-07-23 16:15:16"	"5"	"TLT.NASDAQ"	"727.33"	"None"',
            '"64407587"	"TBA0174.001"	"TLT.NASDAQ"	"TRADE"	"2020-07-23 16:15:16"	"-844.95"	"USD"	"-727.33"	"None"',
            '"64407588"	"TBA0174.001"	"TLT.NASDAQ"	"COMMISSION"	"2020-07-23 16:15:16"	"-0.1"	"USD"	"-0.09"	"None"',
            '"64407296"	"TBA0174.001"	"IEF.ARCA"	"TRADE"	"2020-07-23 16:14:09"	"8"	"IEF.ARCA"	"842.61"	"None"',
            '"64407297"	"TBA0174.001"	"IEF.ARCA"	"TRADE"	"2020-07-23 16:14:09"	"-978.8"	"USD"	"-842.61"	"None"',
            '"64407298"	"TBA0174.001"	"IEF.ARCA"	"COMMISSION"	"2020-07-23 16:14:09"	"-0.16"	"USD"	"-0.14"	"None"',
            '"64407266"	"TBA0174.001"	"FXF.ARCA"	"TRADE"	"2020-07-23 16:13:36"	"10"	"FXF.ARCA"	"852.54"	"None"',
            '"64407267"	"TBA0174.001"	"FXF.ARCA"	"TRADE"	"2020-07-23 16:13:36"	"-990.3"	"USD"	"-852.54"	"None"',
            '"64407268"	"TBA0174.001"	"FXF.ARCA"	"COMMISSION"	"2020-07-23 16:13:36"	"-0.2"	"USD"	"-0.17"	"None"',
            '"64407183"	"TBA0174.001"	"BIL.ARCA"	"TRADE"	"2020-07-23 16:12:45"	"10"	"BIL.ARCA"	"788.13"	"None"',
            '"64407184"	"TBA0174.001"	"BIL.ARCA"	"TRADE"	"2020-07-23 16:12:45"	"-915.4"	"USD"	"-788.13"	"None"',
            '"64407185"	"TBA0174.001"	"BIL.ARCA"	"COMMISSION"	"2020-07-23 16:12:45"	"-0.2"	"USD"	"-0.17"	"None"',
            '"64404974"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-07-23 16:04:08"	"100"	"PHYS.ARCA"	"1296.17"	"None"',
            '"64404975"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-07-23 16:04:08"	"-1506.0"	"USD"	"-1296.17"	"None"',
            '"64404976"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-07-23 16:04:08"	"-2.0"	"USD"	"-1.72"	"None"',
            '"64401646"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-07-23 15:40:53"	"-8650.0"	"EUR"	"-8650.0"	"None"',
            '"64401648"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-07-23 15:40:53"	"10035.04"	"USD"	"8641.73"	"None"',
            '"64389851"	"TBA0174.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-07-23 14:49:44"	"8650.0"	"EUR"	"8650.0"	"None"',
            '"63683972"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-07-16 14:40:58"	"-1.14"	"USD"	"-0.12"	"Transaction ID 62742808 5.0 shares 2020-07-01 dividend TLT.NASDAQ 0.96 USD (0.191656 per share) tax 0.14 USD (15%)"',
            '"62742974"	"TBA0174.001"	"SHY.ARCA"	"DIVIDEND"	"2020-07-06 11:19:45"	"4.85"	"USD"	"4.29"	"80.0 shares 2020-07-01 dividend SHY.ARCA 4.85 USD (0.060636 per share)"',
            '"62742808"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-07-06 11:18:19"	"0.96"	"USD"	"0.85"	"5.0 shares 2020-07-01 dividend TLT.NASDAQ 0.96 USD (0.191656 per share)"',
            '"62742630"	"TBA0174.001"	"IEF.ARCA"	"DIVIDEND"	"2020-07-06 11:17:33"	"1.32"	"USD"	"1.17"	"12.0 shares 2020-07-01 dividend IEF.ARCA 1.32 USD (0.110052 per share)"',
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
        trader.trade_items(csv_report_lines, 2020)

        # then
        # no exception was raised
