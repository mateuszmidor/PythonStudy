from typing import Optional, Protocol
from datetime import datetime
from decimal import Decimal

from src.domain.currency import Currency


class QuotesProviderProtocol(Protocol):
    def get_average_pln_for_day(self, currency: Currency, date: datetime.date) -> Optional[Decimal]:
        pass
