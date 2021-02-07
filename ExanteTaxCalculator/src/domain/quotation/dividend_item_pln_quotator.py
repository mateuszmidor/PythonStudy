from src.domain.transactions.dividend_item import DividendItem
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol
from src.domain.quotation.working_day_before_quotator import WorkingDayBeforeQuotator


class DividendItemPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotator = WorkingDayBeforeQuotator(quotes_provider)

    def quote(self, item: DividendItem) -> DividendItemPLN:
        dividend_quote_pln, dividend_quotation_date = self._quotator.quote(item.received_dividend.currency, item.date)
        received_dividend_pln = item.received_dividend.amount * dividend_quote_pln

        tax_quote_pln, tax_quotation_date = self._quotator.quote(item.paid_tax.currency, item.date)
        paid_tax_pln = item.paid_tax.amount * tax_quote_pln

        quoted = DividendItemPLN(
            source=item,
            dividend_pln_quotation_date=dividend_quotation_date,
            received_dividend_pln=received_dividend_pln,
            tax_pln_quotation_date=tax_quotation_date,
            paid_tax_pln=paid_tax_pln,
        )

        return quoted
