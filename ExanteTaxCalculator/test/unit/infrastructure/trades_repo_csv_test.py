import unittest
from datetime import datetime
from money import Money
from decimal import Decimal
from typing import List

from src.infrastructure.trades_repo_csv import TradesRepoCSV
from src.infrastructure.errors import InvalidTradeError, CorruptedReportError
from src.domain.transactions import *
from src.utils.capture_exception import capture_exception


class TradesRepoCSVTest(unittest.TestCase):
    def test_read_missing_header_raises_error(self) -> None:
        # given
        report_csv: List[str] = []
        repo = TradesRepoCSV()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, CorruptedReportError)

    def test_read_corrupted_header_raises_error(self) -> None:
        # given
        report_csv = ['"Transaction Numbeeeeer"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"']
        repo = TradesRepoCSV()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, CorruptedReportError)

    def test_read_missing_trade_rows_raises_error(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"3"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, InvalidTradeError)

    def test_read_barter_trade_raises_error(self) -> None:
        """ Trades PHYS for PSLV. This should be CORPORATE ACTION, not TRADE """

        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"100"	"PHYS.ARCA"	"1269.77"	"None"',
            '"2"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"-50"	"PSLV.ARCA"	"-150"	"None"',
            '"3"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        expected_error = capture_exception(repo.load, report_csv)

        # then
        self.assertIsInstance(expected_error, InvalidTradeError)

    def test_read_empty_repo_success(self) -> None:
        # given
        report_csv = ['"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"']
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv)

        # then
        self.assertEqual(len(repo.items), 0)

    def test_read_single_buy_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"100"	"PHYS.ARCA"	"1269.77"	"None"',
            '"2"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"-1426.5"	"USD"	"-1269.77"	"None"',
            '"3"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], BuyItem)
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
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"-70"	"SHY.ARCA"	"-5395.76"	"None"',
            '"2"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"6062.0"	"USD"	"5395.76"	"None"',
            '"3"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-06-29 16:07:33"	"-1.4"	"USD"	"-1.25"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], SellItem)
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
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"4"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"100"	"PHYS.ARCA"	"1269.77"	"Buy"',
            '"5"	"TBA0174.001"	"PHYS.ARCA"	"TRADE"	"2020-06-29 16:10:43"	"-1426.5"	"USD"	"-1269.77"	"Buy"',
            '"6"	"TBA0174.001"	"PHYS.ARCA"	"COMMISSION"	"2020-06-29 16:10:43"	"-2.0"	"USD"	"-1.78"	"Buy"',
            '"1"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"-70"	"SHY.ARCA"	"-5395.76"	"Sell"',
            '"2"	"TBA0174.001"	"SHY.ARCA"	"TRADE"	"2020-06-29 16:07:33"	"6062.0"	"USD"	"5395.76"	"Sell"',
            '"3"	"TBA0174.001"	"SHY.ARCA"	"COMMISSION"	"2020-06-29 16:07:33"	"-1.4"	"USD"	"-1.25"	"Sell"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 2)

        assert isinstance(repo.items[0], SellItem)
        sell_item: SellItem = repo.items[0]
        self.assertEqual(sell_item.asset_name, "SHY.ARCA")
        self.assertEqual(sell_item.amount, Decimal("70"))
        self.assertEqual(sell_item.received, Money("6062.0", "USD"))
        self.assertEqual(sell_item.commission, Money("1.4", "USD"))
        self.assertEqual(sell_item.date, datetime(2020, 6, 29, 16, 7, 33))
        self.assertEqual(sell_item.transaction_id, 1)

        assert isinstance(repo.items[1], BuyItem)
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
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-06-23 14:41:21"	"100.0"	"EUR"	"100.0"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], FundingItem)
        item: FundingItem = repo.items[0]
        self.assertEqual(item.funding_amount, Money("100", "EUR"))
        self.assertEqual(item.date, datetime(2020, 6, 23, 14, 41, 21))
        self.assertEqual(item.transaction_id, 1)

    def test_read_withdrawal_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-06-23 14:41:21"	"-100.5"	"EUR"	"-100.5"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], WithdrawalItem)
        item: WithdrawalItem = repo.items[0]
        self.assertEqual(item.withdrawal_amount, Money("100.5", "EUR"))
        self.assertEqual(item.date, datetime(2020, 6, 23, 14, 41, 21))
        self.assertEqual(item.transaction_id, 1)

    def test_read_exchange_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"10"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-06-24 19:52:01"	"-134.0"	"EUR"	"-134.0"	"None"',
            '"11"	"TBA0174.001"	"EUR/USD.EXANTE"	"TRADE"	"2020-06-24 19:52:01"	"150.68"	"USD"	"133.87"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], ExchangeItem)
        item: ExchangeItem = repo.items[0]
        self.assertEqual(item.exchange_from, Money("134", "EUR"))
        self.assertEqual(item.exchange_to, Money("150.68", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)

    def test_read_buy_autoconversion_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"1300"	"CLR.SGX"	"857.24"	"None"',
            '"2"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"-1388.4"	"SGD"	"-857.24"	"None"',
            '"3"	"TBA0174.001"	"CLR.SGX"	"COMMISSION"	"2020-12-08 06:27:21"	"-2.5"	"SGD"	"-1.54"	"None"',
            '"4"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"1388.4"	"SGD"	"857.24"	"None"',
            '"5"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1040.98"	"USD"	"-858.95"	"None"',
            '"6"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"2.5"	"SGD"	"1.54"	"None"',
            '"7"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1.88"	"USD"	"-1.55"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], BuyItem)
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
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"-100"	"CLR.SGX"	"-67.78"	"None"',
            '"2"	"TBA0174.001"	"CLR.SGX"	"TRADE"	"2020-12-08 06:27:21"	"108.9"	"SGD"	"67.78"	"None"',
            '"3"	"TBA0174.001"	"CLR.SGX"	"COMMISSION"	"2020-12-08 06:27:21"	"-2.5"	"SGD"	"-1.56"	"None"',
            '"4"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-108.9"	"SGD"	"-67.78"	"None"',
            '"5"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"81.72"	"USD"	"67.64"	"None"',
            '"6"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"2.5"	"SGD"	"1.56"	"None"',
            '"7"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-1.89"	"USD"	"-1.56"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], SellItem)
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
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"1"	"TBA0174.001"	"CLR.SGX"	"DIVIDEND"	"2020-12-08 06:27:21"	"31.2"	"SGD"	"19.34"	"1300.0 shares (0.024 per share)"',
            '"2"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"-31.2"	"SGD"	"-19.34"	"1300.0 shares (0.024 per share)"',
            '"3"	"TBA0174.001"	"CLR.SGX"	"AUTOCONVERSION"	"2020-12-08 06:27:21"	"23.4"	"USD"	"19.3"	"1300.0  (0.024 per share)"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("31.2", "SGD"))
        self.assertEqual(item.paid_tax, Money("0", "SGD"))
        self.assertEqual(item.date, datetime(2020, 12, 8, 6, 27, 21))
        self.assertEqual(item.transaction_id, 1)
        self.assertEqual(item.autoconversions[0].conversion_from, Money("31.2", "SGD"))
        self.assertEqual(item.autoconversions[0].conversion_to, Money("23.4", "USD"))

    def test_read_dividend_without_tax_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"Dividend source"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        self.assertEqual(item.paid_tax, Money("0", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Dividend source")

    def test_read_dividend_with_tax_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"10"	"TBA0174.001"	"IEF.NASDAQ"	"DIVIDEND"	"2020-06-24 19:52:01"	"100"	"USD"	"75"	"Dividend source"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15"	"USD"	"-12"	"Tax Comment"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], DividendItem)
        item: DividendItem = repo.items[0]
        self.assertEqual(item.received_dividend, Money("100", "USD"))
        self.assertEqual(item.paid_tax, Money("15", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)
        self.assertEqual(item.comment, "Dividend source")

    def test_read_tax_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"10"	"TBA0174.001"	"TLT.NASDAQ"	"TAX"	"2020-06-24 19:52:01"	"-15.0"	"USD"	"-12.0"	"Tax"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], TaxItem)
        item: TaxItem = repo.items[0]
        self.assertEqual(item.paid_tax, Money("15", "USD"))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)

    def test_read_corporate_action_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"10"	"TBA0174.001"	"IEF.ARCA"	"CORPORATE ACTION"	"2020-06-24 19:52:01"	"-20"	"IEF.ARCA"	"-2027.87"	"IEF.ARCA to IEF.NASDAQ"',
            '"11"	"TBA0174.001"	"IEF.NASDAQ"	"CORPORATE ACTION"	"2020-06-24 19:52:01"	"20"	"IEF.NASDAQ"	"2063.21"	"IEF.ARCA to IEF.NASDAQ"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 1)
        assert isinstance(repo.items[0], CorporateActionItem)
        item: CorporateActionItem = repo.items[0]
        self.assertEqual(item.from_share.symbol, "IEF.ARCA")
        self.assertEqual(item.from_share.amount, Decimal(20))
        self.assertEqual(item.to_share.symbol, "IEF.NASDAQ")
        self.assertEqual(item.to_share.amount, Decimal(20))
        self.assertEqual(item.date, datetime(2020, 6, 24, 19, 52, 1))
        self.assertEqual(item.transaction_id, 10)

    def test_read_input_descending_result_ascending_by_date_success(self) -> None:
        # given
        report_csv = [
            '"Transaction ID"	"Account ID"	"Symbol ID"	"Operation type"	"When"	"Sum"	"Asset"	"EUR equivalent"	"Comment"',
            '"3"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-22 10:30:50"	"100.0"	"EUR"	"100.0"	"None"',
            '"2"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-21 10:30:50"	"100.0"	"EUR"	"100.0"	"None"',
            '"1"	"TBA9999.001"	"None"	"FUNDING/WITHDRAWAL"	"2020-10-20 10:30:50"	"100.0"	"EUR"	"100.0"	"None"',
        ]
        repo = TradesRepoCSV()

        # when
        repo.load(report_csv, "\t")

        # then
        self.assertEqual(len(repo.items), 3)
        self.assertEqual(repo.items[0].transaction_id, 1)
        self.assertEqual(repo.items[1].transaction_id, 2)
        self.assertEqual(repo.items[2].transaction_id, 3)
