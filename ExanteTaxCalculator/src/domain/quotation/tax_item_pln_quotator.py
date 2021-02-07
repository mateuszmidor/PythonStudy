from src.domain.transactions.tax_item import TaxItem
from src.domain.quotation.tax_item_pln import TaxItemPLN
from src.domain.quotation.quotes_provider_protocol import QuotesProviderProtocol
from src.domain.quotation.working_day_before_quotator import WorkingDayBeforeQuotator


class TaxItemPLNQuotator:
    def __init__(self, quotes_provider: QuotesProviderProtocol) -> None:
        self._quotator = WorkingDayBeforeQuotator(quotes_provider)

    def quote(self, item: TaxItem) -> TaxItemPLN:
        tax_quote_pln, tax_quotation_date = self._quotator.quote(item.paid_tax.currency, item.date)
        paid_tax_pln = item.paid_tax.amount * tax_quote_pln

        quoted = TaxItemPLN(
            source=item,
            tax_pln_quotation_date=tax_quotation_date,
            paid_tax_pln=paid_tax_pln,
        )

        return quoted
