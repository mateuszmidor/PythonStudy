import unittest
from typing import Iterable, Tuple, Dict
from decimal import Decimal
from money import Money
from datetime import date
from src.domain.wallet import Wallet
from src.utils.capture_exception import capture_exception
from src.domain.errors import InsufficientAssetError
from src.domain.buy_item import BuyItem
from src.domain.sell_item import SellItem
from src.domain.exchange_item import ExchangeItem
from src.domain.funding_item import FundingItem
from src.domain.withdrawal_item import WithdrawalItem


def make_wallet(initial_assets: Dict[str, str] = {}) -> Wallet:
    d: Dict[str, Decimal] = {}
    for k, v in initial_assets.items():
        d[k] = Decimal(v)
    wallet = Wallet(initial_assets=d)
    return wallet


class WalletTest(unittest.TestCase):
    def test_fund(self) -> None:
        # given
        item = FundingItem(Money("100", "USD"), date(2020, 10, 20), 0)
        wallet = make_wallet()

        # when
        wallet.fund(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("100"))

    def test_withdraw(self) -> None:
        # given
        item = WithdrawalItem(Money("50", "USD"), date(2020, 10, 20), 0)
        wallet = make_wallet({"USD": "100"})

        # when
        wallet.withdraw(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("50"))

    def test_exchange(self) -> None:
        # given
        item = ExchangeItem(Money("50", "USD"), Money("40", "EUR"), date(2020, 10, 20), 1)
        wallet = make_wallet({"USD": "100"})

        # when
        wallet.exchange(item)

        # then
        self.assertTrue("USD" in wallet.assets)
        self.assertEqual(wallet.assets["USD"], Decimal("50"))
        self.assertTrue("EUR" in wallet.assets)
        self.assertEqual(wallet.assets["EUR"], Decimal("40"))

    def test_withdraw_non_owned_asset_raises_error(self) -> None:
        # given
        item = WithdrawalItem(Money("50", "EUR"), date(2020, 10, 20), 0)
        wallet = make_wallet({"USD": "100"})

        # when
        expected_error = capture_exception(wallet.withdraw, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_withdraw_more_than_owned_asset_raises_error(self) -> None:
        # given
        item = WithdrawalItem(Money("150", "USD"), date(2020, 10, 20), 0)
        wallet = make_wallet({"USD": "100"})

        # when
        expected_error = capture_exception(wallet.withdraw, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_exchange_non_owned_asset_raises_error(self) -> None:
        # given
        item = ExchangeItem(Money("50", "USD"), Money("40", "EUR"), date(2020, 10, 20), 1)
        wallet = make_wallet({"THB": "100"})

        # when
        expected_error = capture_exception(wallet.exchange, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_exchange_more_than_owned_asset_raises_error(self) -> None:
        # given
        item = ExchangeItem(Money("50", "USD"), Money("40", "EUR"), date(2020, 10, 20), 1)
        wallet = make_wallet({"USD": "10"})

        # when
        expected_error = capture_exception(wallet.exchange, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_buy(self) -> None:
        # given
        item = BuyItem("PHYS", Decimal("100"), Money("1000", "USD"), Money("2", "USD"), date(2020, 10, 22), 1)
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
        item = BuyItem("PHYS", Decimal("100"), Money("1000", "USD"), Money("2", "USD"), date(2020, 10, 22), 1)
        wallet = make_wallet({"USD": "1000"})

        # when
        expected_error = capture_exception(wallet.buy, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_sell(self) -> None:
        # given
        item = SellItem("PHYS", Decimal("100"), Money("1000", "USD"), Money("2", "USD"), date(2020, 10, 22), 1)
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
        item = SellItem("PHYS", Decimal("100"), Money("1000", "USD"), Money("2", "USD"), date(2020, 10, 22), 1)
        wallet = make_wallet({"PHYS": "50"})

        # when
        expected_error = capture_exception(wallet.sell, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    def test_sell_insufficient_money_raises_error(self) -> None:
        # given
        item = SellItem("PHYS", Decimal("0.1"), Money("1", "USD"), Money("2", "USD"), date(2020, 10, 22), 1)
        wallet = make_wallet({"PHYS": "50"})

        # when
        expected_error = capture_exception(wallet.sell, item)

        # then
        self.assertIsInstance(expected_error, InsufficientAssetError)

    # def test_pay_in(self):
    #     # given
    #     wallet = CurrencyWallet()
    #     money = Money(100, "USD")

    #     # when
    #     wallet.pay_in(money)

    #     # then
    #     self.assertTrue(USD in wallet.currencies)
    #     self.assertEqual(wallet.get(USD), Decimal("100"))

    # def test_pay_in_two_same_currency(self):
    #     # given
    #     wallet = CurrencyWallet()
    #     money1 = Money(100, "USD")
    #     money2 = Money(0.50, "USD")

    #     # when
    #     wallet.pay_in(money1)
    #     wallet.pay_in(money2)

    #     # then
    #     self.assertTrue(USD in wallet.currencies)
    #     self.assertEqual(wallet.get(USD), Decimal("100.50"))

    # def test_pay_in_two_different_currencies(self):
    #     # given
    #     wallet = CurrencyWallet()
    #     money1 = Money(100, "USD")
    #     money2 = Money(1.50, "EUR")

    #     # when
    #     wallet.pay_in(money1)
    #     wallet.pay_in(money2)

    #     # then
    #     self.assertTrue(USD in wallet.currencies)
    #     self.assertEqual(wallet.get(USD), Decimal("100"))
    #     self.assertTrue(EUR in wallet.currencies)
    #     self.assertEqual(wallet.get(EUR), Decimal("1.50"))

    # def test_pay_out(self):
    #     # given
    #     wallet = CurrencyWallet()

    #     # when
    #     wallet.pay_out(Money(100, "USD"))

    #     # then
    #     self.assertTrue(USD in wallet.currencies)
    #     self.assertEqual(wallet.get(USD), Decimal("-100"))

    # def test_pay_out_two_same_currency(self):
    #     # given
    #     wallet = CurrencyWallet()

    #     # when
    #     wallet.pay_out(Money(100, "USD"))
    #     wallet.pay_out(Money(1.50, "USD"))

    #     # then
    #     self.assertTrue(USD in wallet.currencies)
    #     self.assertEqual(wallet.get(USD), Decimal("-101.50"))

    # def test_pay_out_two_different_currencies(self):
    #     # given
    #     wallet = CurrencyWallet()

    #     # when
    #     wallet.pay_out(Money(100, "USD"))
    #     wallet.pay_out(Money(1.50, "EUR"))

    #     # then
    #     self.assertTrue(USD in wallet.currencies)
    #     self.assertEqual(wallet.get(USD), Decimal("-100"))
    #     self.assertTrue(EUR in wallet.currencies)
    #     self.assertEqual(wallet.get(EUR), Decimal("-1.50"))

    # def test_pay_in_pay_out_same_currency(self):
    #     # given
    #     wallet = CurrencyWallet()
    #     money1 = Money(100, "USD")
    #     money2 = Money(0.50, "USD")

    #     # when
    #     wallet.pay_in(money1)
    #     wallet.pay_out(money2)

    #     # then
    #     self.assertTrue(USD in wallet.currencies)
    #     self.assertEqual(wallet.get(USD), Decimal("99.50"))