import unittest
from typing import Iterable, Tuple, Dict
from decimal import Decimal
from money import Money
from datetime import datetime
from src.domain.share import Share
from src.domain.wallet import Wallet
from test.utils.capture_exception import capture_exception
from src.domain.errors import InsufficientAssetError
from src.domain.transactions import *


def make_wallet(initial_assets: Dict[str, str] = {}) -> Wallet:
    d: Dict[str, Decimal] = {}
    for k, v in initial_assets.items():
        d[k] = Decimal(v)
    wallet = Wallet(initial_assets=d)
    return wallet


class WalletTest(unittest.TestCase):
    def test_fund(self) -> None:
        # given
        item = FundingItem(Money("100", "USD"))
        wallet = make_wallet()

        # when
        wallet.fund(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("100"))

    def test_withdraw(self) -> None:
        # given
        item = WithdrawalItem(Money("50", "USD"), datetime(2020, 10, 20), 0)
        wallet = make_wallet({"USD": "100"})

        # when
        wallet.withdraw(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("50"))

    def test_exchange(self) -> None:
        # given
        item = ExchangeItem(exchange_from=Money("50", "USD"), exchange_to=Money("40", "EUR"), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"USD": "100"})

        # when
        wallet.exchange(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("50"))
        self.assertTrue("EUR" in wallet.assets)
        self.assertEqual(wallet.assets["EUR"], Decimal("40"))

    def test_dividend_without_tax(self) -> None:
        # given
        item = DividendItem(received_dividend=Money("100", "USD"), paid_tax=TaxItem(Money("0", "USD")), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"USD": "0"})

        # when
        wallet.dividend(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("100"))

    def test_dividend_with_tax(self) -> None:
        # given
        item = DividendItem(
            received_dividend=Money("100", "USD"),
            paid_tax=TaxItem(Money("15", "USD")),
            date=datetime(2020, 10, 20),
            transaction_id=1,
        )
        wallet = make_wallet({"USD": "0"})

        # when
        wallet.dividend(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("85"))

    def test_tax(self) -> None:
        # given
        item = TaxItem(paid_tax=Money("15", "USD"), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"USD": "100"})

        # when
        wallet.tax(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("85"))

    def test_issuance_fee(self) -> None:
        # given
        item = IssuanceFeeItem(paid_fee=Money("15", "USD"), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"USD": "100"})

        # when
        wallet.issuance_fee(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("85"))

    def test_tax_non_owned_currency_raises_error(self) -> None:
        # given
        item = TaxItem(paid_tax=Money("15", "USD"), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"CAD": "100"})

        # when
        expected_error = capture_exception(wallet.tax, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_tax_more_than_owned_asset_raises_error(self) -> None:
        # given
        item = TaxItem(paid_tax=Money("15", "USD"), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"USD": "10"})

        # when
        expected_error = capture_exception(wallet.tax, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_corporate_action(self) -> None:
        # given
        from_share = Share(amount=Decimal(20), symbol="PHYS.ARCA")
        to_share = Share(amount=Decimal(20), symbol="PHYS.NYSE")
        item = CorporateActionItem(from_share=from_share, to_share=to_share, date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"PHYS.ARCA": "20"})

        # when
        wallet.corporate_action(item)

        # then
        self.assertTrue("PHYS.NYSE" in wallet.assets)
        self.assertEqual(wallet.assets["PHYS.NYSE"], Decimal("20"))
        self.assertEqual(wallet.assets["PHYS.ARCA"], Decimal("0"))

    def test_corporate_action_non_owned_share_raises_error(self) -> None:
        # given
        from_share = Share(amount=Decimal(20), symbol="PHYS.ARCA")
        to_share = Share(amount=Decimal(20), symbol="PHYS.NYSE")
        item = CorporateActionItem(from_share=from_share, to_share=to_share, date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet()

        # when
        expected_error = capture_exception(wallet.corporate_action, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_corporate_action_more_than_owned_share_raises_error(self) -> None:
        # given
        from_share = Share(amount=Decimal(20), symbol="PHYS.ARCA")
        to_share = Share(amount=Decimal(20), symbol="PHYS.NYSE")
        item = CorporateActionItem(from_share=from_share, to_share=to_share, date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"PHYS.ARCA": "10"})

        # when
        expected_error = capture_exception(wallet.corporate_action, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_withdraw_non_owned_asset_raises_error(self) -> None:
        # given
        item = WithdrawalItem(Money("50", "EUR"), datetime(2020, 10, 20), 0)
        wallet = make_wallet({"USD": "100"})

        # when
        expected_error = capture_exception(wallet.withdraw, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_withdraw_more_than_owned_asset_raises_error(self) -> None:
        # given
        item = WithdrawalItem(Money("150", "USD"), datetime(2020, 10, 20), 0)
        wallet = make_wallet({"USD": "100"})

        # when
        expected_error = capture_exception(wallet.withdraw, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_exchange_non_owned_asset_raises_error(self) -> None:
        # given
        item = ExchangeItem(exchange_from=Money("50", "USD"), exchange_to=Money("40", "EUR"), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"THB": "100"})

        # when
        expected_error = capture_exception(wallet.exchange, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_exchange_more_than_owned_asset_raises_error(self) -> None:
        # given
        item = ExchangeItem(exchange_from=Money("50", "USD"), exchange_to=Money("40", "EUR"), date=datetime(2020, 10, 20), transaction_id=1)
        wallet = make_wallet({"USD": "10"})

        # when
        expected_error = capture_exception(wallet.exchange, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    # Autoconversion doesnt seem to be standalone transaction but always follows Buy/Sell/Dividend
    # def test_autoconversion(self) -> None:
    #     # given
    #     item = AutoConversionItem(conversion_from=Money("50", "USD"), conversion_to=Money("40", "EUR"), date=date(2020, 10, 20), transaction_id=1)
    #     wallet = make_wallet({"USD": "100"})

    #     # when
    #     wallet.autoconversion(item)

    #     # then
    #     self.assertTrue("USD" in wallet.assets)
    #     self.assertEqual(wallet.assets["USD"], Decimal("50"))
    #     self.assertTrue("EUR" in wallet.assets)
    #     self.assertEqual(wallet.assets["EUR"], Decimal("40"))

    # Autoconversion doesnt seem to be standalone transaction but always follows Buy/Sell/Dividend
    # def test_autoconversion_non_owned_asset_raises_error(self) -> None:
    #     # given
    #     item = AutoConversionItem(conversion_from=Money("50", "USD"), conversion_to=Money("40", "EUR"), date=date(2020, 10, 20), transaction_id=1)
    #     wallet = make_wallet({"THB": "100"})

    #     # when
    #     expected_error = capture_exception(wallet.autoconversion, item)

    #     # then
    #     self.assertIsInstance(expected_error, InsufficientAssetError)

    # Autoconversion doesnt seem to be standalone transaction but always follows Buy/Sell/Dividend
    # def test_autoconversion_more_than_owned_asset_raises_error(self) -> None:
    #     # given
    #     item = AutoConversionItem(conversion_from=Money("50", "USD"), conversion_to=Money("40", "EUR"), date=date(2020, 10, 20), transaction_id=1)
    #     wallet = make_wallet({"USD": "10"})

    #     # when
    #     expected_error = capture_exception(wallet.autoconversion, item)

    #     # then
    #     self.assertIsInstance(expected_error, InsufficientAssetError)

    #
    def test_buy(self) -> None:
        # given
        item = BuyItem(
            asset_name="PHYS",
            amount=Decimal("100"),
            paid=Money("1000", "USD"),
            commission=Money("2", "USD"),
            date=datetime(2020, 10, 22),
            transaction_id=1,
        )
        wallet = make_wallet({"USD": "1005"})

        # when
        wallet.buy(item)

        # then
        self.assertTrue("PHYS", wallet.assets)
        self.assertEqual(wallet.assets["PHYS"], Decimal("100"))
        self.assertTrue("USD", wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("3"))

    def test_buy_insufficient_money_raises_error(self) -> None:
        # given
        item = BuyItem(
            asset_name="PHYS",
            amount=Decimal("100"),
            paid=Money("1000", "USD"),
            commission=Money("2", "USD"),
            date=datetime(2020, 10, 22),
            transaction_id=1,
        )
        wallet = make_wallet({"USD": "1000"})

        # when
        expected_error = capture_exception(wallet.buy, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_sell(self) -> None:
        # given
        item = SellItem("PHYS", Decimal("100"), Money("1000", "USD"), Money("2", "USD"), [], datetime(2020, 10, 22), 1)
        wallet = make_wallet({"PHYS": "150"})

        # when
        wallet.sell(item)

        # then
        self.assertTrue("PHYS", wallet.assets)
        self.assertEqual(wallet.assets["PHYS"], Decimal("50"))
        self.assertTrue("USD", wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("998"))

    def test_sell_insufficient_asset_raises_error(self) -> None:
        # given
        item = SellItem("PHYS", Decimal("100"), Money("1000", "USD"), Money("2", "USD"), [], datetime(2020, 10, 22), 1)
        wallet = make_wallet({"PHYS": "50"})

        # when
        expected_error = capture_exception(wallet.sell, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_sell_insufficient_money_raises_error(self) -> None:
        # given
        item = SellItem("PHYS", Decimal("0.1"), Money("1", "USD"), Money("2", "USD"), [], datetime(2020, 10, 22), 1)
        wallet = make_wallet({"PHYS": "50"})

        # when
        expected_error = capture_exception(wallet.sell, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)
