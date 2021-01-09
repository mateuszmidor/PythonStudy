from typing import List
from decimal import Decimal
from src.domain.currency import Currency

# from src.domain.currency_wallet import CurrencyWallet
from src.domain.buy_sell_pair import BuySellPair

# class TradingYearlyReport:

#     def __init__(self, currencies: CurrencyWallet) -> None:
#         self._currencies = currencies
#         self.items : List[BuySellPair] = []

#     def get_currency(self, currency : Currency) -> Decimal :
#         return self._currencies.get(currency)

#     def append(self, item: BuySellPair) -> None:
#         self.items.append(item)
