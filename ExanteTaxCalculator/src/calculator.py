import sys
import logging
import datetime
import requests
from http import HTTPStatus
from typing import List, Tuple, Optional
from decimal import Decimal
from functools import lru_cache

from src.domain.currency import Currency
from src.domain.quotation.nbp.quotator_nbp import QuotatorNBP
from src.domain.reporting.trading_report_printer import TradingReportPrinter
from src.domain.reporting.assets_printer import AssetPrettyPrinter
from src.application.trader import Trader

logging.basicConfig(level=logging.INFO)

TAX_PERCENTAGE = Decimal("19.0")


class QuotesProviderStub:
    """ Stub the quotes provider to avoid hitting NBP API when manual testing """

    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        if currency == Currency("USD"):
            return Decimal("4")
        if currency == Currency("SGD"):
            return Decimal("3")

        raise ValueError(f"Expected USD or SGD, got: {currency}")


@lru_cache
def url_fetch(url: str) -> Tuple[str, HTTPStatus]:
    """ Return: (http response body, http response code) """
    try:
        r = requests.get(url)
        return r.text, HTTPStatus(r.status_code)
    except requests.exceptions.HTTPError as err:
        return str(err), err.response.status_code


def csv_read_utf8(filename: str) -> List[str]:
    """ Read csv file lines """
    with open(filename) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    return lines


def print_trader_outcomes(trader: Trader) -> None:
    """ Print all the dividends, taxes, buy-sells that produced owned assets and transactions totals """

    printer = TradingReportPrinter()

    print()
    print(printer.to_text(trader.report))

    print()
    print("AKTYWA:")
    print(AssetPrettyPrinter(trader.owned_asssets))


def run_calculator(csv_name: str, year: int) -> None:
    """
    Calculator needs full transaction history from all the years until now,
    because it validates if transactions are valid (for buy - if we have enough money in wallet to successfuly buy)
     AND eg.:
    1. we buy 100 x PHYS in 2020
    2. we sell 100x PHYS in 2021
    the calculator needs to know the exact date of buy to get PLN quotation from previous working day to calculate the transaction cost
    """

    quotes_provider = QuotatorNBP(fetcher=url_fetch)
    # quotes_provider = QuotesProviderStub()
    csv_report_lines = csv_read_utf8(csv_name)
    trader = Trader(quotes_provider=quotes_provider, tax_percentage=TAX_PERCENTAGE)
    trader.trade_items(csv_report_lines, year)

    print_trader_outcomes(trader)


def main() -> None:
    " Entry point of command installed with: pip install ."
    if len(sys.argv) < 3:
        print("Please provide transaction report CSV and year as parameters")
    else:
        run_calculator(sys.argv[1], int(sys.argv[2]))


if __name__ == "__main__":
    main()
