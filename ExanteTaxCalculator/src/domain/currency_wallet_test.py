import unittest
from decimal import Decimal
from money import Money
from src.domain.currency_wallet import CurrencyWallet
from src.utils.capture_exception import capture_exception
from src.domain.currency import USD


class CurrencyWalletTest(unittest.TestCase):
    def test_pay_in(self):
        # given
        wallet = CurrencyWallet()
        money = Money(100, "USD")

        # when
        wallet.pay_in(money)

        # then
        self.assertEqual(wallet.get(USD), Decimal("100"))

    def test_pay_out(self):
        # given
        wallet = CurrencyWallet()

        # when
        wallet.pay_out(Money(100, "USD"))

        # then
        self.assertEqual(wallet.get(USD), Decimal("-100"))


