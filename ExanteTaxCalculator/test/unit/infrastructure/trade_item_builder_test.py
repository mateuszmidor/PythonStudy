import unittest
from datetime import datetime
from decimal import Decimal
from money import Money

from src.infrastructure.report_row import ReportRow
from src.infrastructure.trade_item_builder import TradeItemBuilder
from src.infrastructure.errors import InvalidReportRowError
from src.domain.transactions import *
from src.domain.share import Share
from src.utils.capture_exception import capture_exception

TRADE = ReportRow.OperationType.TRADE
FUNDING_WITHDRAWAL = ReportRow.OperationType.FUNDING_WITHDRAWAL
COMMISSION = ReportRow.OperationType.COMMISSION
AUTOCONVERSION = ReportRow.OperationType.AUTOCONVERSION
DIVIDEND = ReportRow.OperationType.DIVIDEND
TAX = ReportRow.OperationType.TAX
CORPORATE_ACTION = ReportRow.OperationType.CORPORATE_ACTION

DATE = datetime(2020, 10, 20, 16, 15, 55)


class TradeItemBuilderTest(unittest.TestCase):
    def test_build_buy_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("100"), "PHYS", Decimal("1269.77"), "Buy gold")
        row2 = ReportRow(2, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("-1426.5"), "USD", Decimal("-1269.77"), "Buy gold")
        row3 = ReportRow(3, "ACCOUNT.001", "PHYS", COMMISSION, DATE, Decimal("-2.0"), "USD", Decimal("-1.78"), "Buy gold")

        # when
        item = TradeItemBuilder().add(row1).add(row2).add(row3).build()

        # then
        self.assertIsInstance(item, BuyItem)
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.amount, Decimal("100"))
        self.assertEqual(item.paid, Money("1426.5", "USD"))
        self.assertEqual(item.commission, Money("2.0", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_buy_with_autoconversion_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("100"), "PHYS", Decimal("1269.77"), "Buy gold")
        row2 = ReportRow(2, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("-1426.5"), "USD", Decimal("-1269.77"), "Buy gold")
        row3 = ReportRow(3, "ACCOUNT.001", "PHYS", COMMISSION, DATE, Decimal("-2.0"), "USD", Decimal("-1.78"), "Buy gold")
        row4 = ReportRow(4, "ACCOUNT.001", "NYSE", AUTOCONVERSION, DATE, Decimal("1426.5"), "USD", Decimal("1000"), "Conversion")
        row5 = ReportRow(5, "ACCOUNT.001", "NYSE", AUTOCONVERSION, DATE, Decimal("-1000"), "EUR", Decimal("-1000"), "Conversion")
        row6 = ReportRow(6, "ACCOUNT.001", "NYSE", AUTOCONVERSION, DATE, Decimal("2"), "USD", Decimal("1.5"), "Conversion")
        row7 = ReportRow(7, "ACCOUNT.001", "NYSE", AUTOCONVERSION, DATE, Decimal("-1.5"), "EUR", Decimal("-1.5"), "Conversion")

        # when
        item = TradeItemBuilder().add(row1).add(row2).add(row3).add(row4).add(row5).add(row6).add(row7).build()

        # then
        self.assertIsInstance(item, BuyItem)
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.amount, Decimal("100"))
        self.assertEqual(item.paid, Money("1426.5", "USD"))
        self.assertEqual(item.commission, Money("2.0", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("1000", "EUR"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("1426.5", "USD"))
        self.assertEqual(item.autoconversions[1].conversion_from, Money("1.5", "EUR"))
        self.assertEqual(item.autoconversions[1].conversion_to, Money("2", "USD"))

    def test_build_sell_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("-70"), "SHY", Decimal("-5395.76"), "Sell shy")
        row2 = ReportRow(2, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("6062.0"), "USD", Decimal("5395.76"), "Sell shy")
        row3 = ReportRow(3, "ACCOUNT.001", "SHY", COMMISSION, DATE, Decimal("-1.4"), "USD", Decimal("-1.25"), "Sell shy")

        # when
        item = TradeItemBuilder().add(row1).add(row2).add(row3).build()

        # then
        self.assertIsInstance(item, SellItem)
        self.assertEqual(item.asset_name, "SHY")
        self.assertEqual(item.amount, Decimal("70"))
        self.assertEqual(item.received, Money("6062.0", "USD"))
        self.assertEqual(item.commission, Money("1.4", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_sell_with_autoconversion_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("-70"), "SHY", Decimal("-5395.76"), "Sell shy")
        row2 = ReportRow(2, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("6062.0"), "USD", Decimal("5395.76"), "Sell shy")
        row3 = ReportRow(3, "ACCOUNT.001", "SHY", COMMISSION, DATE, Decimal("-1.4"), "USD", Decimal("-1.25"), "Sell shy")
        row4 = ReportRow(4, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("-6062.0"), "USD", Decimal("-4000"), "Conversion")
        row5 = ReportRow(5, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("4000"), "EUR", Decimal("4000"), "Conversion")
        row6 = ReportRow(6, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("1.4"), "USD", Decimal("1"), "Conversion")
        row7 = ReportRow(7, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("-1"), "EUR", Decimal("-1"), "Conversion")

        # when
        item = TradeItemBuilder().add(row1).add(row2).add(row3).add(row4).add(row5).add(row6).add(row7).build()

        # then
        self.assertIsInstance(item, SellItem)
        self.assertEqual(item.asset_name, "SHY")
        self.assertEqual(item.amount, Decimal("70"))
        self.assertEqual(item.received, Money("6062.0", "USD"))
        self.assertEqual(item.commission, Money("1.4", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("6062", "USD"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("4000", "EUR"))
        self.assertEqual(item.autoconversions[1].conversion_to, Money("1.4", "USD"))
        self.assertEqual(item.autoconversions[1].conversion_from, Money("1", "EUR"))

    def test_build_funding_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "None", FUNDING_WITHDRAWAL, DATE, Decimal("100.50"), "EUR", Decimal("100.50"), "Fund")

        # when
        item = TradeItemBuilder().add(row1).build()

        # then
        self.assertIsInstance(item, FundingItem)
        self.assertEqual(item.funding_amount, Money("100.5", "EUR"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_withdrawal_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "None", FUNDING_WITHDRAWAL, DATE, Decimal("-100.50"), "USD", Decimal("-75.50"), "Fund")

        # when
        item = TradeItemBuilder().add(row1).build()

        # then
        self.assertIsInstance(item, WithdrawalItem)
        self.assertEqual(item.withdrawal_amount, Money("100.5", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_exchange_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "EUR/USD.EXANTE", TRADE, DATE, Decimal("-100.0"), "EUR", Decimal("-100.0"), "Exchange")
        row2 = ReportRow(2, "ACCOUNT.001", "EUR/USD.EXANTE", TRADE, DATE, Decimal("130.0"), "USD", Decimal("100.0"), "Exchange")

        # when
        item = TradeItemBuilder().add(row1).add(row2).build()

        # then
        self.assertIsInstance(item, ExchangeItem)
        self.assertEqual(item.exchange_from, Money("100.0", "EUR"))
        self.assertEqual(item.exchange_to, Money("130.0", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_dividend_without_tax(self) -> None:
        # given
        row = ReportRow(1, "ACCOUNT.001", "IEF.NASDAQ", DIVIDEND, DATE, Decimal("100"), "USD", Decimal("75"), "Dividend")

        # when
        item = TradeItemBuilder().add(row).build()

        # then
        self.assertIsInstance(item, DividendItem)
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        self.assertEqual(item.paid_tax, Money("0", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_dividend_with_tax(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "IEF.NASDAQ", DIVIDEND, DATE, Decimal("100"), "USD", Decimal("75"), "Dividend")
        row2 = ReportRow(2, "ACCOUNT.001", "IEF.NASDAQ", TAX, DATE, Decimal("-15"), "USD", Decimal("-12"), "Tax")

        # when
        item = TradeItemBuilder().add(row1).add(row2).build()

        # then
        self.assertIsInstance(item, DividendItem)
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        self.assertEqual(item.paid_tax, Money("15", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_dividend_with_autoconversion_item(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "CLR.SGX", DIVIDEND, DATE, Decimal("31.2"), "SGD", Decimal("19.34"), "")
        row2 = ReportRow(2, "ACCOUNT.001", "CLR.SGX", AUTOCONVERSION, DATE, Decimal("-31.2"), "SGD", Decimal("-19.34"), "")
        row3 = ReportRow(3, "ACCOUNT.001", "CLR.SGX", AUTOCONVERSION, DATE, Decimal("23.4"), "USD", Decimal("19.3"), "")

        # when
        item = TradeItemBuilder().add(row1).add(row2).add(row3).build()

        # then
        self.assertIsInstance(item, DividendItem)
        self.assertEqual(item.received_dividend, Money("31.2", "SGD"))
        self.assertEqual(item.paid_tax, Money("0", "SGD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("31.2", "SGD"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("23.4", "USD"))

    def test_build_tax(self) -> None:
        # given
        row = ReportRow(1, "ACCOUNT.001", "TLT.NASDAQ", TAX, DATE, Decimal("-15"), "USD", Decimal("-12"), "Tax")

        # when
        item = TradeItemBuilder().add(row).build()

        # then
        self.assertIsInstance(item, TaxItem)
        self.assertEqual(item.paid_tax, Money("15", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_corporate_action(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "TLT.NASDAQ", CORPORATE_ACTION, DATE, Decimal("-15"), "TLT.NASDAQ", Decimal("-12"), "crop action")
        row2 = ReportRow(1, "ACCOUNT.001", "TLT.NASDAQ", CORPORATE_ACTION, DATE, Decimal("15"), "TLT.NYSE", Decimal("-12"), "crop action")

        # when
        item = TradeItemBuilder().add(row1).add(row2).build()

        # then
        self.assertIsInstance(item, CorporateActionItem)
        self.assertEqual(item.from_share, Share(Decimal("15"), "TLT.NASDAQ"))
        self.assertEqual(item.to_share, Share(Decimal("15"), "TLT.NYSE"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    ########################################################### extras

    def test_buy_and_fund_return_two_independent_results(self) -> None:
        # given
        row1 = ReportRow(2, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("100"), "PHYS", Decimal("1269.77"), "Buy gold")
        row2 = ReportRow(3, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("-1426.5"), "USD", Decimal("-1269.77"), "Buy gold")
        row3 = ReportRow(4, "ACCOUNT.001", "PHYS", COMMISSION, DATE, Decimal("-2.0"), "USD", Decimal("-1.78"), "Buy gold")
        row4 = ReportRow(1, "ACCOUNT.001", "None", FUNDING_WITHDRAWAL, DATE, Decimal("100.50"), "EUR", Decimal("100.50"), "Fund")
        builder = TradeItemBuilder()

        # when
        item1 = builder.add(row1).add(row2).add(row3).build()
        item2 = builder.add(row4).build()

        # then
        self.assertIsInstance(item1, BuyItem)
        self.assertIsInstance(item2, FundingItem)

    def test_sell_and_exchange_return_two_independent_results(self) -> None:
        # given
        row1 = ReportRow(3, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("-70"), "SHY", Decimal("-5395.76"), "Sell shy")
        row2 = ReportRow(4, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("6062.0"), "USD", Decimal("5395.76"), "Sell shy")
        row3 = ReportRow(5, "ACCOUNT.001", "SHY", COMMISSION, DATE, Decimal("-1.4"), "USD", Decimal("-1.25"), "Sell shy")
        row4 = ReportRow(1, "ACCOUNT.001", "EUR/USD.EXANTE", TRADE, DATE, Decimal("-100.0"), "EUR", Decimal("-100.0"), "Exchange")
        row5 = ReportRow(2, "ACCOUNT.001", "EUR/USD.EXANTE", TRADE, DATE, Decimal("130.0"), "USD", Decimal("100.0"), "Exchange")
        builder = TradeItemBuilder()

        # when
        item1 = builder.add(row1).add(row2).add(row3).build()
        item2 = builder.add(row4).add(row5).build()

        # then
        self.assertIsInstance(item1, SellItem)
        self.assertIsInstance(item2, ExchangeItem)
