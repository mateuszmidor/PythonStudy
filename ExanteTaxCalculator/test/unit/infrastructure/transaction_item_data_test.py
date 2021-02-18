import unittest
from datetime import datetime
from money import Money
from decimal import Decimal
from typing import List

from src.infrastructure.report_row import ReportRow
from src.infrastructure.transaction_item_data import TransactionItemData
from src.infrastructure.errors import InvalidReportRowError
from src.domain.transactions import *
from test.utils.capture_exception import capture_exception


def newRow(
    sum: Decimal,
    asset: str,
    operation_type: ReportRow.OperationType = ReportRow.OperationType.DIVIDEND,
    transaction_id: int = 1,
) -> ReportRow:
    return ReportRow(
        transaction_id=transaction_id,
        account_id="ACC1",
        symbol_id=asset,
        operation_type=operation_type,
        when=datetime(2001, 1, 1),
        sum=sum,
        asset=asset,
        eur_equivalent=Decimal(7),
        comment="",
    )


class TransactionItemDataTest(unittest.TestCase):
    def test_reset_empties_data(self):
        # given
        row = newRow(sum=10, asset="USD")
        data = TransactionItemData(
            increase=row,
            decrease=row,
            commission=row,
            transaction_id=1,
            autoconversions=[row, row],
        )

        # when
        data.reset()

        # then
        self.assertIsNone(data.increase)
        self.assertIsNone(data.decrease)
        self.assertIsNone(data.commission)
        self.assertIsNone(data.transaction_id)
        self.assertEqual(data.autoconversions, [])

    def test_add_commission_negative_money_sets_commission(self):
        # given
        row = newRow(sum=-10, asset="USD", operation_type=ReportRow.OperationType.COMMISSION)
        data = TransactionItemData()

        # when
        data.add_row(row)

        # then
        self.assertEqual(data.commission.sum, -10)
        self.assertEqual(data.commission.asset, "USD")

    def test_add_commission_positive_money_raises_error(self):
        # given
        row = newRow(sum=10, asset="USD", operation_type=ReportRow.OperationType.COMMISSION)
        data = TransactionItemData()

        # when
        expected_error = capture_exception(data.add_row, row)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_add_commission_non_money_raises_error(self):
        # given
        row = newRow(sum=-10, asset="PHYS", operation_type=ReportRow.OperationType.COMMISSION)
        data = TransactionItemData()

        # when
        expected_error = capture_exception(data.add_row, row)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_add_positive_sets_increase(self):
        # given
        row = newRow(sum=10, asset="PHYS")
        data = TransactionItemData()

        # when
        data.add_row(row)

        # then
        self.assertEqual(data.increase.sum, 10)
        self.assertEqual(data.increase.asset, "PHYS")

    def test_add_negative_sets_decrease(self):
        # given
        row = newRow(sum=-10, asset="PHYS")
        data = TransactionItemData()

        # when
        data.add_row(row)

        # then
        self.assertEqual(data.decrease.sum, -10)
        self.assertEqual(data.decrease.asset, "PHYS")

    def test_add_autoconversion_positive_money_sets_autoconversion_increase(self):
        # given
        row = newRow(sum=10, asset="USD", operation_type=ReportRow.OperationType.AUTOCONVERSION)
        data = TransactionItemData()

        # when
        data.add_row(row)

        # then
        self.assertEqual(data.autoconversions[0].increase.sum, 10)
        self.assertEqual(data.autoconversions[0].increase.asset, "USD")

    def test_add_autoconversion_negative_money_sets_autoconversion_decrease(self):
        # given
        row = newRow(sum=-10, asset="USD", operation_type=ReportRow.OperationType.AUTOCONVERSION)
        data = TransactionItemData()

        # when
        data.add_row(row)

        # then
        self.assertEqual(data.autoconversions[0].decrease.sum, -10)
        self.assertEqual(data.autoconversions[0].decrease.asset, "USD")

    def test_first_added_sets_transaction_id(self):
        # given
        row1 = newRow(sum=10, asset="PHYS", operation_type=ReportRow.OperationType.TRADE, transaction_id=1)
        row2 = newRow(sum=-1000, asset="USD", operation_type=ReportRow.OperationType.TRADE, transaction_id=2)
        row3 = newRow(sum=-3, asset="USD", operation_type=ReportRow.OperationType.COMMISSION, transaction_id=3)
        data = TransactionItemData()

        # when
        data.add_row(row1)
        data.add_row(row2)
        data.add_row(row3)

        # then
        self.assertEqual(data.transaction_id, 1)