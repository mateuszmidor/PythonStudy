from typing import Sequence, Dict, List
from decimal import Decimal
from money import Money
from copy import deepcopy

from src.domain.profit_item import ProfitItem
from src.domain.quotation.buy_sell_pair_pln_quotator import QuotesProviderProtocol
from src.domain.wallet import Wallet
from src.domain.transactions import *
from src.domain.trading.buy_sell_items_matcher import BuySellItemsMatcher
from src.domain.profit_calculator import ProfitCalculator
from src.domain.quotation.buy_sell_pair_pln_quotator import BuySellPairPLNQuotator
from src.domain.quotation.dividend_item_pln_quotator import DividendItemPLNQuotator
from src.domain.quotation.tax_item_pln_quotator import TaxItemPLNQuotator
from src.domain.tax_calculator import TaxCalculator
from src.infrastructure.trades_repo_csv import TradesRepoCSV

from src.domain.reporting.report_item import ReportItem
from src.domain.reporting.trade_report_builder import TradeReportBuilder


class Trader:
    def __init__(self, quotes_provider: QuotesProviderProtocol, tax_percentage: Decimal) -> None:
        self._quotes_provider = quotes_provider
        self._tax_calculator = TaxCalculator(tax_percentage)
        self._wallet = Wallet()
        self._total_profit = Money("0", "PLN")
        self._total_tax = Money("0", "PLN")
        self._tax_already_paid = Money("0", "PLN")
        self._report: List[ReportItem] = []

    def trade_items(self, csv_report_lines: Sequence[str]) -> None:
        repo = TradesRepoCSV()
        repo.load(report_csv_lines=csv_report_lines)
        matcher = BuySellItemsMatcher()
        received_dividends: List[DividendItem] = []
        paid_taxes: List[TaxItem] = []

        for item in repo.items:
            if isinstance(item, FundingItem):
                self._wallet.fund(item)
            elif isinstance(item, ExchangeItem):
                self._wallet.exchange(item)
            elif isinstance(item, BuyItem):
                self._wallet.buy(item)
                matcher.buy(item)
            elif isinstance(item, SellItem):
                self._wallet.sell(item)
                matcher.sell(item)
            elif isinstance(item, AutoConversionItem):
                self._wallet.autoconversion(item)
            elif isinstance(item, DividendItem):
                self._wallet.dividend(item)
                received_dividends.append(item)
            elif isinstance(item, TaxItem):
                self._wallet.tax(item)
                paid_taxes.append(item)
            elif isinstance(item, CorporateActionItem):
                self._wallet.corporate_action(item)
            elif isinstance(item, WithdrawalItem):
                self._wallet.withdraw(item)
            else:
                raise TypeError(f"Not implemented transaction type: {type(item)}")

        # buy-sell profits in PLN
        buy_sell_item_quotator = BuySellPairPLNQuotator(self._quotes_provider)
        buy_sell_pairs_pln = [buy_sell_item_quotator.quote(item) for item in matcher.buy_sell_pairs]
        profit_calculator = ProfitCalculator()
        profit_items_pln = [profit_calculator.calc_profit(item) for item in buy_sell_pairs_pln]
        trade_outcomes_values = [item.profit for item in profit_items_pln]

        # received dividends in PLN
        dividend_quotator = DividendItemPLNQuotator(self._quotes_provider)
        dividend_items_pln = [dividend_quotator.quote(item) for item in received_dividends]
        dividend_values = [item.received_dividend_pln for item in dividend_items_pln]
        dividend_taxes_values = [item.paid_tax_pln for item in dividend_items_pln]

        # paid taxes in PLN
        tax_quotator = TaxItemPLNQuotator(self._quotes_provider)
        tax_items_pln = [tax_quotator.quote(item) for item in paid_taxes]
        freestanding_taxes_values = [item.paid_tax_pln for item in tax_items_pln]

        self._total_profit, self._total_tax, self._tax_already_paid = self._tax_calculator.calc_profit_tax(
            trades=trade_outcomes_values,
            dividends=dividend_values,
            taxes=freestanding_taxes_values + dividend_taxes_values,
        )

        self._report = TradeReportBuilder.build(profits=profit_items_pln, dividends=dividend_items_pln, taxes=tax_items_pln)

    @property
    def owned_asssets(self) -> Dict[str, Decimal]:
        return self._wallet.assets

    @property
    def total_profit(self) -> Money:
        """
        This is the total profit from trades and dividends, before deducting tax.
        Can be negative if transactions resulted in a loss and dividends didn't help.
        """
        return self._total_profit

    @property
    def total_tax(self) -> Money:
        """
        This is the total tax to be paid as a percentage of total profit.
        Always >= 0 PLN
        """
        return self._total_tax

    @property
    def tax_already_paid(self) -> Money:
        """
        This is the tax that was already deducted by the broker (from dividends).
        Always >= 0 PLN
        """
        return self._tax_already_paid

    @property
    def report(self) -> List[ReportItem]:
        return deepcopy(self._report)