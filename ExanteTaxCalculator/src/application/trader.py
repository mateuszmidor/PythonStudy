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
from src.domain.tax_declaration.tax_declaration_numbers_calculator import TaxDeclarationNumbersCalculator
from src.domain.reporting.trading_report import TradingReport
from src.domain.reporting.trading_report_builder import TradingReportBuilder
from src.infrastructure.trades_repo_csv import TradesRepoCSV


class Trader:
    def __init__(self, quotes_provider: QuotesProviderProtocol, tax_percentage: Decimal) -> None:
        self._quotes_provider = quotes_provider
        self._tax_calculator = TaxDeclarationNumbersCalculator(tax_percentage)
        self._wallet = Wallet()
        self._report: TradingReport

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
            elif isinstance(item, AutoConversionItem):  # Autoconversion doesnt seem to be standalone transaction but always follows Buy/Sell/Dividend
                raise TypeError(f"Autoconversion is not expected to be a standalone transaction but so it happened: {type(item)}")
            else:
                raise TypeError(f"Not implemented transaction type: {type(item)}")

        # buy-sell profits in PLN
        buy_sell_item_quotator = BuySellPairPLNQuotator(self._quotes_provider)
        buy_sell_pairs_pln = [buy_sell_item_quotator.quote(item) for item in matcher.buy_sell_pairs]
        profit_calculator = ProfitCalculator()
        profit_items_pln = [profit_calculator.calc_profit(item) for item in buy_sell_pairs_pln]
        buy_values = [item.paid.amount for item in profit_items_pln]
        sell_values = [item.received.amount for item in profit_items_pln]

        # received dividends in PLN
        dividend_quotator = DividendItemPLNQuotator(self._quotes_provider)
        dividend_items_pln = [dividend_quotator.quote(item) for item in received_dividends]
        dividend_values = [item.received_dividend_pln for item in dividend_items_pln]

        # paid taxes in PLN
        tax_quotator = TaxItemPLNQuotator(self._quotes_provider)
        tax_items_pln = [tax_quotator.quote(item) for item in paid_taxes]  # collect standalone taxes
        tax_items_pln += [item.paid_tax_pln for item in dividend_items_pln if item.paid_tax_pln is not None]  # add taxes tied to dividends
        tax_values = [item.paid_tax_pln for item in tax_items_pln]

        results = self._tax_calculator.calc_tax_declaration_numbers(buys=buy_values, sells=sell_values, dividends=dividend_values, taxes=tax_values)

        self._report = TradingReportBuilder.build(
            profits=profit_items_pln,
            dividends=dividend_items_pln,
            taxes=tax_items_pln,
            results=results,
        )

    @property
    def owned_asssets(self) -> Dict[str, Decimal]:
        return self._wallet.assets

    @property
    def report(self) -> TradingReport:
        return deepcopy(self._report)