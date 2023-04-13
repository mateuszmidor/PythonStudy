from typing import Sequence, Dict, List, Tuple
from decimal import Decimal
from money import Money
from copy import deepcopy

from src.domain.profit_item import ProfitItem
from src.domain.quotation.buy_sell_pair_pln_quotator import QuotesProviderProtocol
from src.domain.wallet import Wallet
from src.domain.transactions import *
from src.domain.trading.buy_sell_fifo_matcher import BuySellFIFOMatcher
from src.domain.trading.buy_sell_pair import BuySellPair
from src.domain.money_flow_calculator import BuySellMoneyFlowCalculator
from src.domain.quotation.buy_sell_pair_pln import BuySellPairPLN
from src.domain.quotation.buy_sell_pair_pln_quotator import BuySellPairPLNQuotator
from src.domain.quotation.dividend_item_pln_quotator import DividendItemPLNQuotator
from src.domain.quotation.tax_item_pln_quotator import TaxItemPLNQuotator
from src.domain.tax_declaration.tax_declaration_numbers_calculator import TaxDeclarationNumbersCalculator
from src.domain.reporting.trading_report import TradingReport
from src.domain.reporting.trading_report_builder import TradingReportBuilder
from src.infrastructure.trades_repo_csv_2 import TradesRepoCSV2


class Trader:
    def __init__(self, quotes_provider: QuotesProviderProtocol, tax_percentage: Decimal) -> None:
        self._quotes_provider = quotes_provider
        self._tax_calculator = TaxDeclarationNumbersCalculator(tax_percentage)
        self._wallet = Wallet()
        self._report: TradingReport

    def trade_items(self, report_csv_lines: Sequence[str], year: int) -> None:
        repo = TradesRepoCSV2()
        repo.load(report_csv_lines=report_csv_lines)
        matcher = BuySellFIFOMatcher()
        received_dividends: List[DividendItem] = []
        paid_taxes: List[TaxItem] = []

        for i, item in enumerate(repo.items):
            # print(i, item)
            if isinstance(item, FundingItem):
                self._wallet.fund(item)
            elif isinstance(item, ExchangeItem):
                self._wallet.exchange(item)
            elif isinstance(item, BuyItem):
                self._wallet.buy(item)
                matcher.buy(item)
            elif isinstance(item, SellItem):  # generates numbers for PIT38 - check year here
                self._wallet.sell(item)
                if item.date.year == year:
                    matcher.sell(item)
            elif isinstance(item, DividendItem):  # generates numbers for PIT38 - check year here
                self._wallet.dividend(item)
                if item.date.year == year:
                    received_dividends.append(item)
            elif isinstance(item, TaxItem):  # generates numbers for PIT38 - check year here
                self._wallet.tax(item)
                if item.date.year == year:
                    paid_taxes.append(item)
            elif isinstance(item, IssuanceFeeItem):
                self._wallet.issuance_fee(item)
            elif isinstance(item, CorporateActionItem):
                self._wallet.corporate_action(item)
                matcher.corporate_action(item)
            elif isinstance(item, StockSplitItem):
                self._wallet.stock_split(item)
                matcher.stock_split(item)
            elif isinstance(item, WithdrawalItem):
                self._wallet.withdraw(item)
            elif isinstance(item, AutoConversionItem):
                self._wallet.autoconversion(item)
                # in 2023 report it turned out autoconversion can be a standalone transaction.
                # before it was:
                # raise TypeError(f"Autoconversion is not expected to be a standalone transaction but so it happened: {type(item)}")
            else:
                raise TypeError(f"Not implemented transaction type: {type(item)}")

        # money flow generated from buy/sell pairs in PLN
        money_flow_pln, buy_amounts, sell_amounts = self._get_buys_sells(matcher.buy_sell_pairs)

        # received dividends in PLN
        dividend_quotator = DividendItemPLNQuotator(self._quotes_provider)
        dividend_items_pln = [dividend_quotator.quote(item) for item in received_dividends]
        dividend_amounts = [item.received_dividend_pln for item in dividend_items_pln]

        # paid taxes in PLN
        tax_quotator = TaxItemPLNQuotator(self._quotes_provider)
        tax_items_pln = [tax_quotator.quote(item) for item in paid_taxes]  # collect standalone taxes
        tax_items_pln += [item.paid_tax_pln for item in dividend_items_pln if item.paid_tax_pln is not None]  # add taxes reported with dividends
        tax_amounts = [item.paid_tax_pln for item in tax_items_pln]

        results = self._tax_calculator.calc_tax_declaration_numbers(buys=buy_amounts, sells=sell_amounts, dividends=dividend_amounts, taxes=tax_amounts)

        self._report = TradingReportBuilder.build(
            profits=money_flow_pln,
            dividends=dividend_items_pln,
            taxes=tax_items_pln,
            results=results,
        )

    def _get_buys_sells(self, buy_sell_pairs: List[BuySellPair]) -> Tuple[List[ProfitItem], List[Decimal], List[Decimal]]:
        buy_sell_item_quotator = BuySellPairPLNQuotator(self._quotes_provider)
        buy_sell_pairs_pln = [buy_sell_item_quotator.quote(item) for item in buy_sell_pairs]
        money_flow_calculator = BuySellMoneyFlowCalculator()
        money_flow_pln = [money_flow_calculator.calc_money_flow(item) for item in buy_sell_pairs_pln]
        buy_values = [item.paid.amount for item in money_flow_pln]
        sell_values = [item.received.amount for item in money_flow_pln]
        return money_flow_pln, buy_values, sell_values

    @property
    def owned_asssets(self) -> Dict[str, Decimal]:
        return self._wallet.assets_copy

    @property
    def report(self) -> TradingReport:
        return deepcopy(self._report)
