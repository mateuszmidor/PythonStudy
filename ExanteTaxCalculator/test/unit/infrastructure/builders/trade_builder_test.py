from src.infrastructure.report_row import ReportRow
import unittest
from datetime import datetime
from decimal import Decimal
from money import Money
import pytest
from src.domain.transactions import *
from src.infrastructure.builders.trade_builder import TradeBuilder

TRADE = ReportRow.OperationType.TRADE
FUNDING_WITHDRAWAL = ReportRow.OperationType.FUNDING_WITHDRAWAL
COMMISSION = ReportRow.OperationType.COMMISSION
AUTOCONVERSION = ReportRow.OperationType.AUTOCONVERSION
DIVIDEND = ReportRow.OperationType.DIVIDEND
TAX = ReportRow.OperationType.TAX
US_TAX=ReportRow.OperationType.US_TAX
CORPORATE_ACTION = ReportRow.OperationType.CORPORATE_ACTION
ISSUANCE_FEE = ReportRow.OperationType.ISSUANCE_FEE
STOCK_SPLIT = ReportRow.OperationType.STOCK_SPLIT

DATE = datetime(2020, 10, 20, 16, 15, 55)


class TradeBuilderTest(unittest.TestCase):
    def test_build_buy_item_success(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("100"), "PHYS", Decimal("1269.77"), "Buy gold")
        row2 = ReportRow(2, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("-1426.5"), "USD", Decimal("-1269.77"), "Buy gold")
        row3 = ReportRow(3, "ACCOUNT.001", "PHYS", COMMISSION, DATE, Decimal("-2.0"), "USD", Decimal("-1.78"), "Buy gold")

        # when
        b = TradeBuilder()
        b.add(row1)
        b.add(row2)
        b.add(row3)
        item = b.build()

        # then
        assert isinstance(item, BuyItem)
        self.assertIsInstance(item, BuyItem)
        self.assertEqual(item.asset_name, "PHYS")
        self.assertEqual(item.amount, Decimal("100"))
        self.assertEqual(item.paid, Money("1426.5", "USD"))
        self.assertEqual(item.commission, Money("2.0", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)
        self.assertFalse(b.add(row1))  # cant add another TRADE
        self.assertFalse(b.add(row3))  # cant add another COMMISSION

    # @pytest.mark.skip(reason="no way of currently testing this")
    def test_build_buy_item_with_autoconversion_success(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("100"), "PHYS", Decimal("1269.77"), "Buy gold")
        row2 = ReportRow(2, "ACCOUNT.001", "PHYS", TRADE, DATE, Decimal("-1426.5"), "USD", Decimal("-1269.77"), "Buy gold")
        row3 = ReportRow(3, "ACCOUNT.001", "PHYS", COMMISSION, DATE, Decimal("-2.0"), "USD", Decimal("-1.78"), "Buy gold")
        row4 = ReportRow(4, "ACCOUNT.001", "PHYS", AUTOCONVERSION, DATE, Decimal("1426.5"), "USD", Decimal("1000"), "Conversion")
        row5 = ReportRow(5, "ACCOUNT.001", "PHYS", AUTOCONVERSION, DATE, Decimal("-1000"), "EUR", Decimal("-1000"), "Conversion")
        row6 = ReportRow(6, "ACCOUNT.001", "PHYS", AUTOCONVERSION, DATE, Decimal("2"), "USD", Decimal("1.5"), "Conversion")
        row7 = ReportRow(7, "ACCOUNT.001", "PHYS", AUTOCONVERSION, DATE, Decimal("-1.5"), "EUR", Decimal("-1.5"), "Conversion")

        # when
        b = TradeBuilder()
        b.add(row1)
        b.add(row2)
        b.add(row3)
        b.add(row4)
        b.add(row5)
        b.add(row6)
        b.add(row7)
        item = b.build()

        # then
        assert isinstance(item, BuyItem)
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
        self.assertFalse(b.add(row7))  # cant add another AUTOCONVERSION

    def test_build_sell_item_success(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("-70"), "SHY", Decimal("-5395.76"), "Sell shy")
        row2 = ReportRow(2, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("6062.0"), "USD", Decimal("5395.76"), "Sell shy")
        row3 = ReportRow(3, "ACCOUNT.001", "SHY", COMMISSION, DATE, Decimal("-1.4"), "USD", Decimal("-1.25"), "Sell shy")

        # when
        b = TradeBuilder()
        b.add(row1)
        b.add(row2)
        b.add(row3)
        item = b.build()

        # then
        assert isinstance(item, SellItem)
        self.assertIsInstance(item, SellItem)
        self.assertEqual(item.asset_name, "SHY")
        self.assertEqual(item.amount, Decimal("70"))
        self.assertEqual(item.received, Money("6062.0", "USD"))
        self.assertEqual(item.commission, Money("1.4", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)

    def test_build_sell_item_with_autoconversion_success(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("-70"), "SHY", Decimal("-5395.76"), "Sell shy")
        row2 = ReportRow(2, "ACCOUNT.001", "SHY", TRADE, DATE, Decimal("6062.0"), "USD", Decimal("5395.76"), "Sell shy")
        row3 = ReportRow(3, "ACCOUNT.001", "SHY", COMMISSION, DATE, Decimal("-1.4"), "USD", Decimal("-1.25"), "Sell shy")
        row4 = ReportRow(4, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("-6062.0"), "USD", Decimal("-4000"), "Conversion")
        row5 = ReportRow(5, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("4000"), "EUR", Decimal("4000"), "Conversion")
        row6 = ReportRow(6, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("1.4"), "USD", Decimal("1"), "Conversion")
        row7 = ReportRow(7, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("-1"), "EUR", Decimal("-1"), "Conversion")

        # when
        b = TradeBuilder()
        b.add(row1)
        b.add(row2)
        b.add(row3)
        b.add(row4)
        b.add(row5)
        b.add(row6)
        b.add(row7)
        item = b.build()

        # then
        assert isinstance(item, SellItem)
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

    def test_build_exchange_item_success(self) -> None:
        # given
        row1 = ReportRow(1, "ACCOUNT.001", "EUR/USD.EXANTE", TRADE, DATE, Decimal("-100.0"), "EUR", Decimal("-100.0"), "Exchange")
        row2 = ReportRow(2, "ACCOUNT.001", "EUR/USD.EXANTE", TRADE, DATE, Decimal("130.0"), "USD", Decimal("100.0"), "Exchange")
        row7 = ReportRow(7, "ACCOUNT.001", "SHY", AUTOCONVERSION, DATE, Decimal("-1"), "EUR", Decimal("-1"), "Conversion")

        # when
        b = TradeBuilder()
        b.add(row1)
        b.add(row2)
        item = b.build()

        # then
        assert isinstance(item, ExchangeItem)
        self.assertIsInstance(item, ExchangeItem)
        self.assertEqual(item.exchange_from, Money("100.0", "EUR"))
        self.assertEqual(item.exchange_to, Money("130.0", "USD"))
        self.assertEqual(item.date, DATE)
        self.assertEqual(item.transaction_id, 1)
        self.assertFalse(b.add(row7))  # cant add another AUTOCONVERSION
