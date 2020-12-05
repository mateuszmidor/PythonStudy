from src.domain.trading_yearly_report import TradingYearlyReport
from src.domain.currency_wallet import CurrencyWallet

class Trader:
    def __init__(self) -> None:
        self.items = []

    def report(self) -> TradingYearlyReport:
        wallet = CurrencyWallet()
        return TradingYearlyReport(wallet)

