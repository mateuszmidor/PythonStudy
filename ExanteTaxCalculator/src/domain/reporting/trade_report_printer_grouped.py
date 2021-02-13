from typing import List, Dict
from decimal import Decimal
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field

from money import Money

from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.reporting.report_item import ReportItem


@dataclass
class ReportItemGroup:
    """ Represents a group of assets eg. SHY.ARCA, PHYS.NYSE, TAX, DIVIDEND """

    sum_income: Decimal = Decimal(0)  # PLN, >= 0
    sum_cost: Decimal = Decimal(0)  # PLN, >= 0
    items: List[str] = field(default_factory=list)  # Printable BuySellPair/Dividend/Tax


class TradeReportPrinterGrouped:
    def __init__(self) -> None:
        self._items: Dict[str, ReportItemGroup]

    def to_strings(self, report_items: List[ReportItem]) -> List[str]:
        self._items = dict()

        for item in report_items:
            if isinstance(item, ProfitPLN):
                self.format_profit(item)
            elif isinstance(item, DividendItemPLN):
                self.format_dividend(item)
            elif isinstance(item, TaxItemPLN):
                self.format_tax(item)
            else:
                self._append(f"Expected ReportItem, got: {item}", "ERRORS", Decimal(0), Decimal(0))

        lines: List[str] = []
        group_names = sorted(self._items.keys())
        for group_name in group_names:
            # group title
            lines.append(group_name)

            # group items
            group = self._items[group_name]
            lines.extend(group.items)

            # group summary
            format_str = "Przychód: {:0.2f}. Koszt: {:0.2f}. Z/S: {:0.2f}"
            totals = format_str.format(group.sum_income, group.sum_cost, group.sum_income - group.sum_cost)
            lines.append(totals)
            lines.append("")

        return lines

    def to_text(self, report: List[ReportItem]) -> str:
        return "\n".join(self.to_strings(report))

    def _append(self, item: str, name: str, paid, received: Decimal) -> None:
        if name not in self._items:
            self._items[name] = ReportItemGroup()
        group = self._items[name]
        group.items.append(item)
        group.sum_cost += paid
        group.sum_income += received

    def format_profit(self, item: ProfitPLN) -> None:
        # Z/S:    -1.87 PLN, Ilość: 10, KUPNO:   915.60 USD * 3.7400 PLN/USD =  3424.34 PLN (2020-06-29, D-1: 2020-06-28), SPRZEDAŻ:   915.10 USD * 3.7400 PLN/USD =  3422.47 PLN (2020-07-24, D-1: 2020-07-23)
        format_str = "Z/S: {:8.2f} PLN, Ilość: {:>5}, KUPNO: {:8.2f} {} * {:0.4f} PLN/{} = {:8.2f} PLN ({:%Y-%m-%d}, D-1: {:%Y-%m-%d}), SPRZEDAŻ: {:8.2f} {} * {:0.4f} PLN/{} = {:8.2f} PLN ({:%Y-%m-%d}, D-1: {:%Y-%m-%d})"
        buy_quotation = item.source.buy_paid_pln / item.source.source.buy.paid.amount
        sell_quotation = item.source.sell_received_pln / item.source.source.sell.received.amount
        profit_str = format_str.format(
            item.received.amount - item.paid.amount,
            item.source.source.amount_sold,
            # KUPNO
            item.paid.amount / buy_quotation,
            item.source.source.buy.paid.currency,
            buy_quotation,
            item.source.source.buy.paid.currency,
            item.paid.amount,
            item.source.source.buy.date,
            item.source.buy_pln_quotation_date,
            # SPRZEDAŻ
            item.received.amount / sell_quotation,
            item.source.source.sell.received.currency,
            sell_quotation,
            item.source.source.sell.received.currency,
            item.received.amount,
            item.source.source.sell.date,
            item.source.sell_pln_quotation_date,
        )
        self._append(profit_str, item.source.source.sell.asset_name, item.paid.amount, item.received.amount)

    def format_tax(self, item: TaxItemPLN) -> None:
        self._format_tax(
            tax_pln=item.paid_tax_pln,
            tax=item.source.paid_tax,
            when=item.source.date,
            pln_quotation_date=item.tax_pln_quotation_date,
            comment=item.source.comment,
        )

    def format_dividend(self, item: DividendItemPLN) -> None:
        # Z/S:     4.94 PLN =     1.32 USD * 3.7400 PLN/USD (2020-07-06, D-1: 2020-07-05), 12.0 shares 2020-07-01 dividend IEF.ARCA 1.32 USD (0.110052 per share)
        format_str = "Z/S: {:8.2f} PLN = {:8.2f} {} * {:0.4f} PLN/{} ({:%Y-%m-%d}, D-1: {:%Y-%m-%d}), {}"
        dividend_quotation = item.received_dividend_pln / item.source.received_dividend.amount
        dividend_str = format_str.format(
            item.received_dividend_pln,
            item.source.received_dividend.amount,
            item.source.received_dividend.currency,
            dividend_quotation,
            item.source.received_dividend.currency,
            item.source.date,
            item.dividend_pln_quotation_date,
            item.source.comment,
        )
        self._append(dividend_str, "1. DYWIDENDY", Decimal(0), item.received_dividend_pln)
        if item.paid_tax_pln != 0:
            self._format_tax(
                tax_pln=item.paid_tax_pln,
                tax=item.source.paid_tax,
                when=item.source.date,
                pln_quotation_date=item.tax_pln_quotation_date,
            )

    def _format_tax(self, tax_pln: Decimal, tax: Money, when: datetime, pln_quotation_date: datetime, comment: str = "") -> None:
        # Z/S:    -0.52 PLN =    -0.14 USD * 3.7400 PLN/USD (2020-07-16, D-1: 2020-07-15)
        format_str = "Z/S: {:8.2f} PLN = {:8.2f} {} * {:0.4f} PLN/{} ({:%Y-%m-%d}, D-1: {:%Y-%m-%d}), {}"
        tax_quotation = tax_pln / tax.amount
        tax_string = format_str.format(
            -tax_pln,
            -tax.amount,
            tax.currency,
            tax_quotation,
            tax.currency,
            when,
            pln_quotation_date,
            comment,
        )
        self._append(tax_string, "2. PODATKI", tax_pln, Decimal(0))
