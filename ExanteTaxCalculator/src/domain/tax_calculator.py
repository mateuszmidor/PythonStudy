from money import Money
from  currency_wallet import CurrencyWallet
from trading_yearly_report import TradingYearlyReport

class TaxCalculator:

    def __init__(self):
        self._currencies = CurrencyWallet()

    def fund(self, money: Money):
        self._currencies[money.currency] += money.amount

    def withdraw(self, m : Money):
        owned_amount = self._currencies[m.currency]
        needed_amount = m.amount
        if needed_amount > owned_amount:
            raise ValueError(f"insufficient founds for withrawal of {m}")
        
        self._currencies[m.currency] -= m.amount

    def report(self) -> TradingYearlyReport:
        return TradingYearlyReport(self._currencies)