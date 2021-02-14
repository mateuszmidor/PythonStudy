from typing import List, Dict

from src.domain.profit_item import ProfitPLN
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.reporting.trade_report import TradeReport
from src.domain.tax_calculator import CalculationResult


class TradeReportPrinterGrouped:
    def to_text(self, report: TradeReport) -> str:
        report_lines = self.to_strings(report)
        return "\n".join(report_lines)

    def to_strings(self, report: TradeReport) -> List[str]:
        lines: List[str] = list()

        lines += self._format_dividends(report.dividends)
        lines += self._format_taxes(report.taxes)
        lines += self._format_profits(report.profits)
        lines += self._format_results(report.results)

        return lines

    def _format_profits(self, profits: Dict[str, List[ProfitPLN]]) -> List[str]:
        """ profits are grouped by asset name, eg. profits from selling PHYS.ARCA are grouped under "PHYS.ARCA" """

        format_str = "Przychód: {:0.2f} PLN. Koszt: {:0.2f} PLN. Z/S: {:0.2f} PLN\n"
        result: List[str] = list()

        group_names = sorted(profits.keys())
        for group_name in group_names:
            # group title
            result.append(group_name)

            # group items
            group = profits[group_name]
            result.extend([self._format_profit(item) for item in group])

            # group summary
            sum_cost = sum([item.paid.amount for item in group])
            sum_income = sum([item.received.amount for item in group])
            totals = format_str.format(sum_income, sum_cost, sum_income - sum_cost)
            result.append(totals)

        return result

    def _format_dividends(self, dividends: List[DividendItemPLN]) -> List[str]:
        format_str = "Suma: {:0.2f} PLN\n"
        result: List[str] = list()

        # title
        result.append("DYWIDENDY")

        # items
        result.extend([self._format_dividend(item) for item in dividends])

        # summary
        sum_income = sum([item.received_dividend_pln for item in dividends])
        totals = format_str.format(sum_income)
        result.append(totals)

        return result

    def _format_taxes(self, taxes: List[TaxItemPLN]) -> List[str]:
        format_str = "Suma: {:0.2f} PLN\n"
        result: List[str] = list()

        # title
        result.append("PODATKI OD DYWIDEND ZAPŁACONE ZA GRANICĄ")

        # items
        result.extend([self._format_tax(item) for item in taxes])

        # summary
        sum_cost = sum([item.paid_tax_pln for item in taxes])
        totals = format_str.format(sum_cost)
        result.append(totals)

        return result

    def _format_results(self, results: CalculationResult) -> List[str]:
        result: List[str] = list()

        def print(s: str = "") -> None:
            result.append(s)

        print("WYNIKI (kupno/sprzedaż):")
        print(f"przychód:                     {results.shares_total_income}")
        print(f"koszty uzyskania przychodu:   {results.shares_total_cost}")
        print(f"dochód/strata:                {results.shares_total_income - results.shares_total_cost}")
        print(f"podatek do zapłaty:           {results.shares_total_tax} ({results.tax_percentage_used}%)")

        print()
        print("WYNIKI (dywidendy):")
        print(f"przychód:                     {results.dividends_total_income}")
        print(f"podatek od przychodu:         {results.dividends_total_tax} ({results.tax_percentage_used}%)")
        print(f"podatek zapłacony za granicą: {results.dividends_tax_already_paid}")
        print(f"podatek do zapłaty:           {results.dividends_tax_yet_to_be_paid}")

        return result

    def _format_profit(self, item: ProfitPLN) -> str:
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
        return profit_str

    def _format_tax(self, item: TaxItemPLN) -> str:
        # KWOTA:    -0.52 PLN =    -0.14 USD * 3.7400 PLN/USD (2020-07-16, D-1: 2020-07-15)
        format_str = "KWOTA: {:8.2f} PLN = {:8.2f} {} * {:0.4f} PLN/{} ({:%Y-%m-%d}, D-1: {:%Y-%m-%d}), {}"
        tax_quotation = item.paid_tax_pln / item.source.paid_tax.amount
        tax_string = format_str.format(
            item.paid_tax_pln,
            item.source.paid_tax.amount,
            item.source.paid_tax.currency,
            tax_quotation,
            item.source.paid_tax.currency,
            item.source.date,
            item.tax_pln_quotation_date,
            item.source.comment,
        )
        return tax_string

    def _format_dividend(self, item: DividendItemPLN) -> str:
        # KWOTA:     4.94 PLN =     1.32 USD * 3.7400 PLN/USD (2020-07-06, D-1: 2020-07-05), 12.0 shares 2020-07-01 dividend IEF.ARCA 1.32 USD (0.110052 per share)
        format_str = "KWOTA: {:8.2f} PLN = {:8.2f} {} * {:0.4f} PLN/{} ({:%Y-%m-%d}, D-1: {:%Y-%m-%d}), {}"
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
        return dividend_str
