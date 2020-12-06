from typing import List
from decimal import Decimal
from src.domain.currency import Currency
from src.domain.currency_wallet import CurrencyWallet
from src.domain.tax_item import TaxItem

class TradingYearlyReport:

    def __init__(self, currencies: CurrencyWallet) -> None:
        self._currencies = currencies
        self.items : List[TaxItem] = []

    def get_currency(self, currency : Currency) -> Decimal :
        return self._currencies.get(currency)

    def append(self, item: TaxItem) -> None:
        self.items.append(item)
