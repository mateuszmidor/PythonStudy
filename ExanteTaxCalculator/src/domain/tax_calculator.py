from money import Money
from src.domain.currency_wallet import CurrencyWallet
from src.domain.trading_yearly_report import TradingYearlyReport

class TaxCalculator:

    def __init__(self):
        self._currencies = CurrencyWallet()

    def fund(self, money: Money):
        self._currencies.pay_in(money)

    def withdraw(self, m : Money):
        owned_amount = self._currencies.get(m.currency)
        needed_amount = m.amount
        if needed_amount > owned_amount:
            raise ValueError(f"insufficient funds for withrawal of {m}")
        
        self._currencies.pay_out(m.amount)

    def report(self) -> TradingYearlyReport:
        return TradingYearlyReport(self._currencies)