from money import Money
from src.domain.currency import Currency
from src.domain.currency_wallet import CurrencyWallet
from src.domain.trading_yearly_report import TradingYearlyReport

class TaxCalculator:

    def __init__(self):
        self._currencies = CurrencyWallet()

    def fund(self, money: Money):
        self._currencies.pay_in(money)

    def withdraw(self, m : Money):
        currency = Currency(m.currency)
        owned_amount = self._currencies.get(currency)
        needed_amount = m.amount
        if needed_amount > owned_amount:
            raise ValueError(f"insufficient funds for withrawal of {m}")
        
        self._currencies.pay_out(m)

    def report(self) -> TradingYearlyReport:
        return TradingYearlyReport(self._currencies)