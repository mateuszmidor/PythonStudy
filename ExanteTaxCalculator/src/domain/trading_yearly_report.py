from decimal import Decimal
from src.domain.currency import Currency
from src.domain.currency_wallet import CurrencyWallet

class TradingYearlyReport:

    def __init__(self, currencies: CurrencyWallet):
        self._currencies = currencies

    def get_currency(self, currency : Currency) -> Decimal :
        return self._currencies.get(currency)