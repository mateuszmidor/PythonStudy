from src.domain.transactions.dividend_item import DividendItem
from src.domain.quotation.dividend_item_pln import DividendItemPLN
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol
from src.domain.quotation.working_day_before_quotator import WorkingDayBeforeQuotator
from src.domain.quotation.tax_item_pln_quotator import TaxItemPLNQuotator


class DividendItemPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotator = WorkingDayBeforeQuotator(quotes_provider)
        self._tax_item_quotator = TaxItemPLNQuotator(quotes_provider)

    def quote(self, item: DividendItem) -> DividendItemPLN:
        dividend_quote_pln, dividend_quotation_date = self._quotator.quote(item.received_dividend.currency, item.date)
        received_dividend_pln = item.received_dividend.amount * dividend_quote_pln

        tax_pln = self._tax_item_quotator.quote(item.paid_tax) if item.paid_tax is not None else None

        quoted = DividendItemPLN(
            source=item,
            dividend_pln_quotation_date=dividend_quotation_date,
            received_dividend_pln=received_dividend_pln,
            paid_tax_pln=tax_pln,
        )

        return quoted
