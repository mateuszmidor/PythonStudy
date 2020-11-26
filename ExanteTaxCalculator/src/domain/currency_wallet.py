from decimal import Decimal
from money import Money
from typing import DefaultDict
from src.domain.currency import Currency

class CurrencyWallet(object):
    """ CurrencyWallet represents a collectio of [currency, amount] pairs with default amount of 0.0 for each currency """
    
    def __init__(self):
        self._currencies = DefaultDict(Decimal)

    def get(self, currency : Currency) -> Decimal:
        return self._currencies[currency]

    def pay_in(self, m : Money):
        currency = Currency(m.currency)
        self._currencies[currency] += m.amount

    def pay_out(self, m : Money):
        currency = Currency(m.currency)
        self._currencies[currency] -= m.amount