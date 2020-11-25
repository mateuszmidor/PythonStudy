from decimal import Decimal
from currency_wallet import CurrencyWallet

class TradingYearlyReport:

    def __init__(self, currencies: CurrencyWallet):
        self._currencies = currencies

    def get_currency(self, currency : str) -> Decimal :
        return self._currencies[currency]