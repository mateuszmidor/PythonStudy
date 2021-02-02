import sys
import urllib.request
from http import HTTPStatus
from typing import List, Tuple, Optional
from decimal import Decimal
import datetime
from functools import cache


from src.application.trader import Trader
from src.domain.quotation.nbp.quotator_nbp import QuotatorNBP
from src.domain.reporting.trade_report_printer import TradeReportPrinter
from src.domain.currency import Currency

TAX_PERCENTAGE = Decimal("19.0")


class QuotesProviderStub:
    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        if currency != Currency("USD"):
            raise ValueError(f"Expected USD, got: {currency}")
        return Decimal("3.74")


@cache
def url_fetch(url: str) -> Tuple[str, HTTPStatus]:
    try:
        with urllib.request.urlopen(url) as response:
            return response.read(), HTTPStatus.OK
    except urllib.request.HTTPError as err:
        return err.read(), err.code


def csv_read(filename: str) -> List[str]:
    with open(filename) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    return lines


def run_calculator(csv_name: str) -> None:
    csv_report_lines = csv_read(csv_name)
    # quotes_provider = QuotatorNBP(fetcher=url_fetch)
    quotes_provider = QuotesProviderStub()
    trader = Trader(quotes_provider=quotes_provider, tax_percentage=TAX_PERCENTAGE)

    trader.trade_items(csv_report_lines)

    printer = TradeReportPrinter()

    print()
    print("REPORT:")
    print(printer.to_text(trader.report))

    print()
    print("ASSETS:")
    print(trader.owned_asssets)

    print()
    print("RESULTS:")
    print("total profit (before tax):", trader.total_profit)
    print(f"total tax ({TAX_PERCENTAGE}% of total profit):", trader.total_tax)
    print("already paid tax:", trader.tax_already_paid)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide transaction report CSV as parameter")
    else:
        run_calculator(sys.argv[1])