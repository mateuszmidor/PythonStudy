from decimal import Decimal
from dataclasses import dataclass


@dataclass(frozen=True)
class Share:
    """ Share represents stocks eg. 15 units of PHYS """

    amount: Decimal
    symbol: str

    def __add__(self, other):
        if other.symbol != self.symbol:
            raise TypeError(f"Trying to add different types: {self.symbol} + {other.symbol}")
        return Share(self.amount + other.amount, self.symbol)

    def __str__(self) -> str:
        return f"{self.symbol} {self.amount}"
