from decimal import Decimal

class Asset(object):
    def __init__(self, amount: Decimal, symbol: str):
        self._amount = amount
        self._symbol = symbol

    def __add__(self, other):
        if other._symbol != self._symbol:
            raise ValueError(f"Trying to add different assets: {self._symbol} + {other._symbol}")
        return Asset(self._amount + other._amount, self._symbol)

    def amount(self) -> Decimal:
        return self._amount   

    def symbol(self) -> str:
        return self._symbol