import datetime
from dataclasses import dataclass

from src.domain.share import Share


@dataclass(frozen=True)
class CorporateActionItem:
    from_share: Share
    to_share: Share
    # common transaction item data
    date: datetime.date = datetime.date(1970, 1, 1)
    transaction_id: int = 0
