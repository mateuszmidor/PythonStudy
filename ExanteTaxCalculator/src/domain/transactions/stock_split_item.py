from datetime import datetime
from dataclasses import dataclass

from src.domain.share import Share


@dataclass(frozen=True)
class StockSplitItem:
    """Eg. Split PHYS 1 to 5. Or the other way round 5 to 1"""

    from_share: Share
    to_share: Share
    # common transaction item data
    date: datetime = datetime(1970, 1, 1)
    transaction_id: int = 0
