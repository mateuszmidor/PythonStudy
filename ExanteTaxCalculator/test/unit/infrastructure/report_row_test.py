import unittest
from datetime import datetime
from decimal import Decimal

from src.infrastructure.report_row import ReportRow
from test.utils.capture_exception import capture_exception
from src.infrastructure.errors import InvalidReportRowError


class ReportRowTest(unittest.TestCase):
    def test_from_dict_success(self):
        # given
        dic = {
            "Transaction ID": "62368459",
            "Account ID": "TBA0174.001",
            "Symbol ID": "PHYS.ARCA",
            "Operation type": "TRADE",
            "When": "2020-06-29 16:10:43",
            "Sum": "100.5",
            "Asset": "PHYS.ARCA",
            "EUR equivalent": "1269.77",
            "Comment": "Buy 100.5 units of PHYS",
        }

        # when
        row = ReportRow.from_dict(dic)

        # then
        self.assertEqual(row.transaction_id, 62368459)
        self.assertEqual(row.account_id, "TBA0174.001")
        self.assertEqual(row.symbol_id, "PHYS.ARCA")
        self.assertEqual(row.operation_type, ReportRow.OperationType.TRADE)
        self.assertEqual(row.when, datetime(2020, 6, 29, 16, 10, 43))
        self.assertEqual(row.sum, Decimal("100.5"))
        self.assertEqual(row.asset, "PHYS.ARCA")
        self.assertEqual(row.eur_equivalent, Decimal("1269.77"))
        self.assertEqual(row.comment, "Buy 100.5 units of PHYS")

    def test_from_dict_missing_transactionid_raises_error(self):
        # given
        dic = {
            # "Transaction ID": "123",
            "Account ID": "TBA0174.001",
            "Symbol ID": "PHYS.ARCA",
            "Operation type": "TRADE",
            "When": "2020-06-29 16:10:43",
            "Sum": "100.5",
            "Asset": "PHYS.ARCA",
            "EUR equivalent": "1269.77",
            "Comment": "Buy 100.5 units of PHYS",
        }

        # when
        expected_error = capture_exception(ReportRow.from_dict, dic)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_from_dict_invalid_transactionid_raises_error(self):
        # given
        dic = {
            "Transaction ID": "123ABC",
            "Account ID": "TBA0174.001",
            "Symbol ID": "PHYS.ARCA",
            "Operation type": "TRADE",
            "When": "2020-06-29 16:10:43",
            "Sum": "100.5",
            "Asset": "PHYS.ARCA",
            "EUR equivalent": "1269.77",
            "Comment": "Buy 100.5 units of PHYS",
        }

        # when
        expected_error = capture_exception(ReportRow.from_dict, dic)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_from_dict_empty_accountid_raises_error(self):
        # given
        dic = {
            "Transaction ID": "123",
            "Account ID": "",
            "Symbol ID": "PHYS.ARCA",
            "Operation type": "TRADE",
            "When": "2020-06-29 16:10:43",
            "Sum": "100.5",
            "Asset": "PHYS.ARCA",
            "EUR equivalent": "1269.77",
            "Comment": "Buy 100.5 units of PHYS",
        }

        # when
        expected_error = capture_exception(ReportRow.from_dict, dic)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_from_dict_empty_symbolid_raises_error(self):
        # given
        dic = {
            "Transaction ID": "123",
            "Account ID": "TBA0174.001",
            "Symbol ID": "",
            "Operation type": "TRADE",
            "When": "2020-06-29 16:10:43",
            "Sum": "100.5",
            "Asset": "PHYS.ARCA",
            "EUR equivalent": "1269.77",
            "Comment": "Buy 100.5 units of PHYS",
        }

        # when
        expected_error = capture_exception(ReportRow.from_dict, dic)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_from_dict_empty_asset_raises_error(self):
        # given
        dic = {
            "Transaction ID": "62368459",
            "Account ID": "TBA0174.001",
            "Symbol ID": "PHYS.ARCA",
            "Operation type": "TRADE",
            "When": "2020-06-29 16:10:43",
            "Sum": "100.5",
            "Asset": "",
            "EUR equivalent": "1269.77",
            "Comment": "Buy 100.5 units of PHYS",
        }

        # when
        expected_error = capture_exception(ReportRow.from_dict, dic)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_from_dict_ivalid_operation_type_raises_error(self):
        # given
        dic = {
            "Transaction ID": "123",
            "Account ID": "TBA0174.001",
            "Symbol ID": "PHYS.ARCA",
            "Operation type": "CHARITY",
            "When": "2020-06-29 16:10:43",
            "Sum": "100.5",
            "Asset": "PHYS.ARCA",
            "EUR equivalent": "1269.77",
            "Comment": "Buy 100.5 units of PHYS",
        }

        # when
        expected_error = capture_exception(ReportRow.from_dict, dic)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)

    def test_from_dict_sum_zero_raises_error(self):
        # given
        dic = {
            "Transaction ID": "123",
            "Account ID": "TBA0174.001",
            "Symbol ID": "PHYS.ARCA",
            "Operation type": "TRADE",
            "When": "2020-06-29 16:10:43",
            "Sum": "0",
            "Asset": "PHYS.ARCA",
            "EUR equivalent": "0",
            "Comment": "Buy 0 units of PHYS",
        }

        # when
        expected_error = capture_exception(ReportRow.from_dict, dic)

        # then
        self.assertIsInstance(expected_error, InvalidReportRowError)