from typing import List
from decimal import Decimal
from datetime import datetime

from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.reporting.report_item import ReportItem


class TradeReportPrinter:
    def __init__(self) -> None:
        self._items: List[str] = []

    def to_strings(self, report_items: List[ReportItem]) -> List[str]:
        self._items = []

        for item in report_items:
            if isinstance(item, ProfitPLN):
                self.format_profit(item)
            elif isinstance(item, DividendItemPLN):
                self.format_dividend(item)
            elif isinstance(item, TaxItemPLN):
                self.format_tax(item)
            else:
                self._append(f"Expected ReportItem, got: {item}")

        return self._items

    def to_text(self, report: List[ReportItem]) -> str:
        return "\n".join(self.to_strings(report))

    def _append(self, item: str) -> None:
        self._items.append(item)

    def format_profit(self, item: ProfitPLN) -> None:
        format_str = "{: <20}{:10.4f} PLN, Date: {:%d-%m-%Y %H:%M:%S}, {} x {}, PLN/USD buy: {:0.4f}, PLN/USD sell: {:0.4f}, Buy Q Date: {:%d-%m-%Y}, Sell Q Date: {:%d-%m-%Y}"
        profit_str = format_str.format(
            "BUY/SELL Profit: ",
            item.profit.amount,
            item.source.source.sell.date,
            item.source.source.amount_sold,
            item.source.source.sell.asset_name,
            item.source.buy_paid_pln / item.source.source.buy.paid.amount,
            item.source.sell_received_pln / item.source.source.sell.received.amount,
            item.source.buy_pln_quotation_date,
            item.source.sell_pln_quotation_date,
        )
        self._append(profit_str)

    def format_tax(self, item: TaxItemPLN) -> None:
        tax_str = _format_tax(
            tax_pln=item.paid_tax_pln,
            when=item.source.date,
            pln_quotation_value=item.paid_tax_pln / item.source.paid_tax.amount,
            pln_quotation_date=item.tax_pln_quotation_date,
        )
        self._append(tax_str)

    def format_dividend(self, item: DividendItemPLN) -> None:
        format_str = "{: <20}{:10.4f} PLN, Date: {:%d-%m-%Y %H:%M:%S}, PLN/USD: {:0.4f}, Q Date: {:%d-%m-%Y} {}"
        dividend_str = format_str.format(
            "DIVIDEND Received: ",
            item.received_dividend_pln,
            item.source.date,
            item.received_dividend_pln / item.source.received_dividend.amount,
            item.dividend_pln_quotation_date,
            item.source.comment,
        )
        self._append(dividend_str)
        if item.paid_tax_pln != 0:
            tax_str = _format_tax(
                tax_pln=item.paid_tax_pln,
                when=item.source.date,
                pln_quotation_value=item.paid_tax_pln / item.source.paid_tax.amount,
                pln_quotation_date=item.tax_pln_quotation_date,
            )
            self._append(tax_str)


def _format_tax(tax_pln: Decimal, when: datetime, pln_quotation_value: Decimal, pln_quotation_date: datetime) -> str:
    return "{: <20}{:10.4f} PLN, Date: {:%d-%m-%Y %H:%M:%S}, PLN/USD: {:0.4f}, Q Date: {:%d-%m-%Y}".format(
        "TAX Paid: ",
        tax_pln,
        when,
        pln_quotation_value,
        pln_quotation_date,
    )
