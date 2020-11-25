from decimal import Decimal
from typing import DefaultDict

class CurrencyWallet(DefaultDict[str, Decimal]):
    """ CurrencyWallet represents a collectio of [currency, amount] pairs with default amount of 0.0 for each currency """
    
    def __init__(self):
        super(CurrencyWallet, self).__init__(Decimal) # ensure default of 0

    def __setitem__(self, key : str, value: Decimal):
        if len(key) != 3:
            raise TypeError(f"Currency code should be 3 characters:, got {key}")

        if value < 0.0:
            raise ValueError(f"Currency value should be >= 0, got: {value}")

        super(CurrencyWallet, self).__setitem__(key, value)