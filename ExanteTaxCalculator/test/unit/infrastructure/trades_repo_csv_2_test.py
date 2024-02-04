import unittest
from datetime import datetime
from money import Money
from decimal import Decimal
from typing import List

from src.infrastructure.trades_repo_csv_2 import TradesRepoCSV2
from src.infrastructure.errors import InvalidTradeError, CorruptedReportError
from src.domain.transactions import *
from test.utils.capture_exception import capture_exception


class TradesRepoCSVTest(unittest.TestCase):
    def test_read_missing_header_raises_error(self) -> None:
        # given
        report_csv: List[str] = []
        repo = TradesRepoCSV2()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, CorruptedReportError)

    def test_read_corrupted_header_raises_error(self) -> None:
        # given
        report_csv = ['"Transaction Numbeeeeer"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"']
        repo = TradesRepoCSV2()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, CorruptedReportError)

    def test_read_missing_trade_rows_raises_error(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"3"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, InvalidTradeError)

    def test_read_barter_trade_raises_error(self) -> None:
        """Trades PHYS for PSLV. This should be CORPORATE ACTION, not TRADE"""

        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"3"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"None"',
            '"2"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"-50"	"PSLV.ARCA"	"-150"	"None"',
            '"1"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"100"	"PHYS.ARCA"	"1269.77"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, InvalidTradeError)

    def test_read_empty_repo_success(self) -> None:
        # given
        report_csv = ['"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"']
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv)

        # then
        self.assertEqual(len(repo.items), 0)

    def test_read_extra_column_success(self) -> None:
        # given
        # ISIN is the extra column
        report_csv = ['"Transaction ID"	"Account ID"	"Symbol ID"	"ISIN"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"']
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv)

        # then
        self.assertEqual(len(repo.items), 0)

    def test_read_single_buy_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"3"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"None"',
            '"2"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"-1426.5"	"USD"	"-1269.77"	"None"',
            '"1"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"100"	"PHYS.ARCA"	"1269.77"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], BuyItem)  # plain assert so mypy doesnt complain below
        item: BuyItem = repo.items[0]
        self.assertEqual(item.asset_name, "PHYS.ARCA")
        self.assertEqual(item.amount, Decimal("100"))
        self.assertEqual(item.paid, Money("1426.5", "USD"))
        self.assertEqual(item.commission, Money("2.0", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 29, 16, 10, 43))
        self.assertEqual(item.transaction_id, 1)

    def test_read_single_sell_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"3"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-06-29 16:07:33"	"-1.4"	"USD"	"-1.25"	"None"',
            '"2"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"6062.0"	"USD"	"5395.76"	"None"',
            '"1"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"-70"	"SHY.ARCA"	"-5395.76"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], SellItem)  # plain assert so mypy doesnt complain below
        item: SellItem = repo.items[0]
        self.assertEqual(item.asset_name, "SHY.ARCA")
        self.assertEqual(item.amount, Decimal("70"))
        self.assertEqual(item.received, Money("6062.0", "USD"))
        self.assertEqual(item.commission, Money("1.4", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 29, 16, 7, 33))
        self.assertEqual(item.transaction_id, 1)

    def test_read_buy_sell_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"6"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"Buy"',
            '"5"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"-1426.5"	"USD"	"-1269.77"	"Buy"',
            '"4"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"100"	"PHYS.ARCA"	"1269.77"	"Buy"',
            '"3"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-06-29 16:07:33"	"-1.4"	"USD"	"-1.25"	"Sell"',
            '"2"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"6062.0"	"USD"	"5395.76"	"Sell"',
            '"1"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"-70"	"SHY.ARCA"	"-5395.76"	"Sell"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 2)

        assert isinstance(repo.items[0], SellItem)  # plain assert so mypy doesnt complain below
        sell_item: SellItem = repo.items[0]
        self.assertEqual(sell_item.asset_name, "SHY.ARCA")
        self.assertEqual(sell_item.amount, Decimal("70"))
        self.assertEqual(sell_item.received, Money("6062.0", "USD"))
        self.assertEqual(sell_item.commission, Money("1.4", "USD"))
        self.assertEqual(sell_item.date, datetime(2020, 6, 29, 16, 7, 33))
        self.assertEqual(sell_item.transaction_id, 1)

        assert isinstance(repo.items[1], BuyItem)  # plain assert so mypy doesnt complain below
        buy_item: BuyItem = repo.items[1]
        self.assertEqual(buy_item.asset_name, "PHYS.ARCA")
        self.assertEqual(buy_item.amount, Decimal("100"))
        self.assertEqual(buy_item.paid, Money("1426.5", "USD"))
        self.assertEqual(buy_item.commission, Money("2.0", "USD"))
        self.assertEqual(buy_item.date, datetime(2020, 6, 29, 16, 10, 43))
        self.assertEqual(buy_item.transaction_id, 4)

    def test_read_funding_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"1"	"TBA0174.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-06-23 14:41:21"	"100.0"	"EUR"	"100.0"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], FundingItem)  # plain assert so mypy doesnt complain below
        item: FundingItem = repo.items[0]
        self.assertEqual(item.funding_amount, Money("100", "EUR"))
        self.assertEqual(item.date, datetime(2020, 6, 23, 14, 41, 21))
        self.assertEqual(item.transaction_id, 1)

    def test_read_withdrawal_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"1"	"TBA0174.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-06-23 14:41:21"	"-100.5"	"EUR"	"-100.5"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], WithdrawalItem)  # plain assert so mypy doesnt complain below
        item: WithdrawalItem = repo.items[0]
        self.assertEqual(item.withdrawal_amount, Money("100.5", "EUR"))
        self.assertEqual(item.date, datetime(2020, 6, 23, 14, 41, 21))
        self.assertEqual(item.transaction_id, 1)

    def test_read_exchange_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"11"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-06-24 19:52:01"	"-134.0"	"EUR"	"-134.0"	"None"',
            '"10"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-06-24 19:52:01"	"150.68"	"USD"	"133.87"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], ExchangeItem)  # plain assert so mypy doesnt complain below
        item: ExchangeItem = repo.items[0]
        self.assertEqual(item.exchange_from, Money("134", "EUR"))
        self.assertEqual(item.exchange_to, Money("150.68", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)

    def test_read_buy_autoconversion_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"7"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1.88"	"USD"	"-1.55"	"None"',
            '"6"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"2.5"	"SGD"	"1.54"	"None"',
            '"5"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1040.98"	"USD"	"-858.95"	"None"',
            '"4"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"1388.4"	"SGD"	"857.24"	"None"',
            '"3"	"TBA0174.001"	"CLR.SGX"	"COMMISSION"	"2020-12-08 06:27:21"	"-2.5"	"SGD"	"-1.54"	"None"',
            '"2"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"-1388.4"	"SGD"	"-857.24"	"None"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"1300"	"CLR.SGX"	"857.24"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], BuyItem)  # plain assert so mypy doesnt complain below
        item: BuyItem = repo.items[0]
        self.assertEqual(item.asset_name, "CLR.SGX")
        self.assertEqual(item.amount, Decimal("1300"))
        self.assertEqual(item.paid, Money("1388.4", "SGD"))
        self.assertEqual(item.commission, Money("2.5", "SGD"))
        self.assertEqual(item.date, datetime(2020, 12, 8, 6, 27, 21))
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("1040.98", "USD"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("1388.4", "SGD"))
        self.assertEqual(item.autoconversions[1].conversion_from, Money("1.88", "USD"))
        self.assertEqual(item.autoconversions[1].conversion_to, Money("2.5", "SGD"))

    # AUTOCONVERSION with symbol None is new in 2023, used to be same symbol as for TRADE. No autoconversion is linked to trade with Parent UUID
    def test_read_buy_autoconversion_link_by_uuid_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"1300"	"CLR.SGX"	"857.24"	"None"	"aaa"	""',
            '"2"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"-1388.4"	"SGD"	"-857.24"	"None"	"aaa"	""',
            '"3"	"TBA0174.001"	"CLR.SGX"	"COMMISSION"	"2020-12-08 06:27:21"	"-2.5"	"SGD"	"-1.54"	"None"	"bbb"	""',
            '"4"	"TBA0174.001"	"None"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"1388.4"	"SGD"	"857.24"	"None"	"ccc"	"aaa"',
            '"5"	"TBA0174.001"	"None"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1040.98"	"USD"	"-858.95"	"None"	"ccc"	"aaa"',
            '"6"	"TBA0174.001"	"None"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"2.5"	"SGD"	"1.54"	"None"	"ccc"	"aaa"',
            '"7"	"TBA0174.001"	"None"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1.88"	"USD"	"-1.55"	"None"	"ccc"	"aaa"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], BuyItem)  # plain assert so mypy doesnt complain below
        item: BuyItem = repo.items[0]
        self.assertEqual(item.asset_name, "CLR.SGX")
        self.assertEqual(item.amount, Decimal("1300"))
        self.assertEqual(item.paid, Money("1388.4", "SGD"))
        self.assertEqual(item.commission, Money("2.5", "SGD"))
        self.assertEqual(item.date, datetime(2020, 12, 8, 6, 27, 21))
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("1040.98", "USD"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("1388.4", "SGD"))
        self.assertEqual(item.autoconversions[1].conversion_from, Money("1.88", "USD"))
        self.assertEqual(item.autoconversions[1].conversion_to, Money("2.5", "SGD"))

    def test_read_sell_autoconversion_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"7"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1.89"	"USD"	"-1.56"	"None"',
            '"6"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"2.5"	"SGD"	"1.56"	"None"',
            '"5"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"81.72"	"USD"	"67.64"	"None"',
            '"4"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-108.9"	"SGD"	"-67.78"	"None"',
            '"3"	"TBA0174.001"	"CLR.SGX"	"COMMISSION"	"2020-12-08 06:27:21"	"-2.5"	"SGD"	"-1.56"	"None"',
            '"2"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"108.9"	"SGD"	"67.78"	"None"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"-100"	"CLR.SGX"	"-67.78"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], SellItem)  # plain assert so mypy doesnt complain below
        item: SellItem = repo.items[0]
        self.assertEqual(item.asset_name, "CLR.SGX")
        self.assertEqual(item.amount, Decimal("100"))
        self.assertEqual(item.received, Money("108.9", "SGD"))
        self.assertEqual(item.commission, Money("2.5", "SGD"))
        self.assertEqual(item.date, datetime(2020, 12, 8, 6, 27, 21))
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("108.9", "SGD"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("81.72", "USD"))
        self.assertEqual(item.autoconversions[1].conversion_from, Money("1.89", "USD"))
        self.assertEqual(item.autoconversions[1].conversion_to, Money("2.5", "SGD"))

    def test_read_dividend_autoconversion_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"3"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"23.4"	"USD"	"19.3"	"1300.0  (0.024 per share)"',
            '"2"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-31.2"	"SGD"	"-19.34"	"1300.0 shares (0.024 per share)"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"DIVIDEND"	"2020-12-08 06:27:21"	"31.2"	"SGD"	"19.34"	"1300.0 shares (0.024 per share)"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)  # plain assert so mypy doesnt complain below
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("31.2", "SGD"))
        self.assertIsNone(item.paid_tax)
        self.assertEqual(item.date, datetime(2020, 12, 8, 6, 27, 21))
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("31.2", "SGD"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("23.4", "USD"))

    def test_read_dividend_without_tax_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"Dividend source"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)  # plain assert so mypy doesnt complain below
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        self.assertIsNone(item.paid_tax)
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Dividend source")

    def test_read_dividend_with_tax_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15"	"USD"	"-12"	"Tax Comment"',
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"Dividend source"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)  # plain assert so mypy doesnt complain below
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        assert item.paid_tax is not None  # plain assert so mypy doesnt complain below
        self.assertEqual(item.paid_tax.paid_tax, Money("15", "USD"))
        self.assertEqual(item.paid_tax.comment, "Tax Comment")
        self.assertEqual(item.paid_tax.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Dividend source")

    def test_read_dividend_and_separate_tax_success(self) -> None:
        """dividend and tax are separate because Symbol ID differs"""

        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15"	"USD"	"-12"	"Tax comment"',
            '"10"	"TBA0174.001"	"TLT.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"Dividend source"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 2)
        assert isinstance(repo.items[0], DividendItem)  # plain assert so mypy doesnt complain below
        item1: DividendItem = repo.items[0]
        self.assertEqual(item1.received_dividend, Money("100", "USD"))
        self.assertEqual(item1.transaction_id, 10)
        self.assertEqual(item1.comment, "Dividend source")
        self.assertEqual(item1.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item1.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertIsNone(item1.paid_tax)

        assert isinstance(repo.items[1], TaxItem)  # plain assert so mypy doesnt complain below
        item2: TaxItem = repo.items[1]
        self.assertEqual(item2.paid_tax, Money("15", "USD"))
        self.assertEqual(item2.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item2.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item2.transaction_id, 11)
        self.assertEqual(item2.comment, "Tax comment")

    def test_read_dividend_with_issuance_fee_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"ISSUANCE FEE"	"2020-06-24 19:52:01"	"-15"	"USD"	"-12"	"Issuance Fee Comment"',
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"Dividend source"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)  # plain assert so mypy doesnt complain below
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        self.assertIsNone(item.paid_tax)
        assert item.paid_issuance_fee is not None  # plain assert so mypy doesnt complain below
        self.assertEqual(item.paid_issuance_fee.paid_fee, Money("15", "USD"))
        self.assertEqual(item.paid_issuance_fee.comment, "Issuance Fee Comment")
        self.assertEqual(item.paid_issuance_fee.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Dividend source")

    def test_read_dividend_with_tax_and_issuance_fee_success(self) -> None:
        # TODO: allow dividend parsing with both tax and fee
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"12"	"TBA0174.001"	"IEF.NASDAQ"	"ISSUANCE FEE"	"2020-06-24 19:52:01"	"-5"	"USD"	"-4"	"Issuance Fee Comment"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15"	"USD"	"-12"	"Tax Comment"',
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"Dividend source"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)  # plain assert so mypy doesnt complain below
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Dividend source")

        assert item.paid_tax is not None  # plain assert so mypy doesnt complain below
        self.assertEqual(item.paid_tax.paid_tax, Money("15", "USD"))
        self.assertEqual(item.paid_tax.comment, "Tax Comment")
        self.assertEqual(item.paid_tax.date, datetime(2020, 6, 24, 19, 52, 1))

        assert item.paid_issuance_fee is not None  # plain assert so mypy doesnt complain below
        self.assertEqual(item.paid_issuance_fee.paid_fee, Money("5", "USD"))
        self.assertEqual(item.paid_issuance_fee.comment, "Issuance Fee Comment")
        self.assertEqual(item.paid_issuance_fee.date, datetime(2020, 6, 24, 19, 52, 1))

    def test_read_tax_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"10"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15.0"	"USD"	"-12.0"	"Tax source comment"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], TaxItem)  # plain assert so mypy doesnt complain below
        item: TaxItem = repo.items[0]
        self.assertEqual(item.paid_tax, Money("15", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Tax source comment")

    def test_read_ustax_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"10"	"TBA0174.001"	"TLT.NASDAQ"	"US TAX"	"2020-06-24 19:52:01"	"-15.0"	"USD"	"-12.0"	"Tax source comment"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], TaxItem)  # plain assert so mypy doesnt complain below
        item: TaxItem = repo.items[0]
        self.assertEqual(item.paid_tax, Money("15", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Tax source comment")

    def test_read_issuance_fee_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"10"	"TBA0174.001"	"GSK.NYSE"	"ISSUANCE FEE"	"2020-06-24 19:52:01"	"-15.0"	"USD"	"-12.0"	"Issuance fee comment"',
        ]

        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], IssuanceFeeItem)  # plain assert so mypy doesnt complain below
        item: IssuanceFeeItem = repo.items[0]
        self.assertEqual(item.paid_fee, Money("15", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Issuance fee comment")

    def test_read_corporate_action_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"12"	"TBA0174.001"	"IEF.ARCA"	"CORPORATE ACTION"	"2020-06-24 19:52:01"	"-20"	"IEF.ARCA"	"-2027.87"	"IEF.ARCA to IEF.NASDAQ"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"CORPORATE ACTION"	"2020-06-24 19:52:01"	"20"	"IEF.NASDAQ"	"2063.21"	"IEF.ARCA to IEF.NASDAQ"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], CorporateActionItem)  # plain assert so mypy doesnt complain below
        item: CorporateActionItem = repo.items[0]
        self.assertEqual(item.from_share.symbol, "IEF.ARCA")
        self.assertEqual(item.from_share.amount, Decimal(20))
        self.assertEqual(item.to_share.symbol, "IEF.NASDAQ")
        self.assertEqual(item.to_share.amount, Decimal(20))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 11)

    def test_read_stock_split_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"ISIN"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"12"	"TBA0174.001"	"2768.TSE"	"JP3663900003"	"STOCK SPLIT"	"2021-09-29 06:56:01"	"20"	"2768.TSE"	"241.08"	"Stock split 1 for 5"	"0e26b166-3481-417c-9d9e-df9ce55b2dfb"	"None"',
            '"11"	"TBA0174.001"	"2768.TSE"	"JP3663900003"	"STOCK SPLIT"	"2021-09-29 06:55:58"	"-100"	"2768.TSE"	"-241.09"	"Stock split 1 for 5"	"ca9396da-7d1d-4b08-a6b1-6d6af49687ef"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], StockSplitItem)
        item: StockSplitItem = repo.items[0]
        self.assertEqual(item.from_share.symbol, "2768.TSE")
        self.assertEqual(item.from_share.amount, Decimal(100))
        self.assertEqual(item.to_share.symbol, "2768.TSE")
        self.assertEqual(item.to_share.amount, Decimal(20))
        self.assertEqual(item.date, datetime(2021, 9, 29, 6, 55, 58))
        self.assertEqual(item.transaction_id, 11)

    def test_read_input_descending_result_ascending_by_date_and_transactionid_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"4"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-22 10:30:50"	"50.0"	"EUR"	"50.0"	"None"',
            '"3"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-22 10:30:50"	"100.0"	"EUR"	"100.0"	"None"',
            '"2"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-21 10:30:50"	"100.0"	"EUR"	"100.0"	"None"',
            '"1"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 10:30:50"	"100.0"	"EUR"	"100.0"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 4)
        self.assertEqual(repo.items[0].transaction_id, 1)
        self.assertEqual(repo.items[1].transaction_id, 2)
        self.assertEqual(repo.items[2].transaction_id, 3)
        self.assertEqual(repo.items[3].transaction_id, 4)

    def test_mixed_items_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"12"	"TBA0174.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-06-23 14:41:21"	"100.0"	"EUR"	"100.0"	"None"',
            '"11"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15.0"	"USD"	"-12.0"	"Tax source comment"',
            '"10"	"TBA0174.001"	"GSK.NYSE"	"ISSUANCE FEE"	"2020-06-24 19:52:01"	"-15.0"	"USD"	"-12.0"	"Issuance fee comment"',
        ]

        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 3)
        assert isinstance(repo.items[0], IssuanceFeeItem)  # plain assert so mypy doesnt complain below
        item: IssuanceFeeItem = repo.items[0]
        self.assertEqual(item.paid_fee, Money("15", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Issuance fee comment")

        assert isinstance(repo.items[1], TaxItem)
        assert isinstance(repo.items[2], FundingItem)

    def test_read_standaolne_autoconversion_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"7"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1.88"	"USD"	"-1.55"	"None"',
            '"6"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"2.5"	"SGD"	"1.54"	"None"',
        ]
        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], AutoConversionItem)  # plain assert so mypy doesnt complain below
        item: AutoConversionItem = repo.items[0]
        self.assertEqual(item.date, datetime(2020, 12, 8, 6, 27, 21))
        self.assertEqual(item.transaction_id, 6)
        self.assertEqual(item.conversion_from, Money("1.88", "USD"))
        self.assertEqual(item.conversion_to, Money("2.5", "SGD"))

    def test_rollback_transactions_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"	"UUID"	"Parent UUID"',
            '"6"	"TBA0174.001"	"GSK.NYSE"	"AUTOCONVERSION"	"2022-02-18 08:11:35"	"0.06"	"EUR"	"0.06"	"Rollback for transaction #2 2022-02-17 21:46:44.957"',
            '"5"	"TBA0174.001"	"GSK.NYSE"	"AUTOCONVERSION"	"2022-02-18 08:11:35"	"-0.06"	"USD"	"-0.05"	"Rollback for transaction #3 2022-02-17 21:46:44.957"',
            '"4"	"TBA0174.001"	"GSK.NYSE"	"ISSUANCE FEE"	"2022-02-18 08:11:35"	"-0.06"	"EUR"	"-0.06"	"Rollback for transaction #1 2022-02-17 21:46:44.957"',
            '"3"	"TBA0174.001"	"GSK.NYSE"	"AUTOCONVERSION"	"2022-02-17 21:46:44"	"0.06"	"USD"	"0.05"	"14 shares ExD 2021-11-18 PD 2022-01-13 dividend GSK.NYSE 7.24 EUR (0.5168342 per share) tax -0.00 EUR (-0.0%) DivCntry GB"',
            '"2"	"TBA0174.001"	"GSK.NYSE"	"AUTOCONVERSION"	"2022-02-17 21:46:44"	"-0.06"	"EUR"	"-0.06"	"14 shares ExD 2021-11-18 PD 2022-01-13 dividend GSK.NYSE 7.24 EUR (0.5168342 per share) tax -0.00 EUR (-0.0%) DivCntry GB"',
            '"1"	"TBA0174.001"	"GSK.NYSE"	"ISSUANCE FEE"	"2022-02-17 21:46:44"	"0.06"	"EUR"	"0.06"	"14 shares ExD 2021-11-18 PD 2022-01-13 dividend GSK.NYSE 7.24 EUR (0.5168342 per share) tax -0.00 EUR (-0.0%) DivCntry GB"',
        ]

        repo = TradesRepoCSV2()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(repo.items, [])
