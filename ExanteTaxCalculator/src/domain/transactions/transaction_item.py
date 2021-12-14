from typing import Union

from src.domain.transactions import *

TransactionItem = Union[
    BuyItem,
    SellItem,
    FundingItem,
    WithdrawalItem,
    ExchangeItem,
    AutoConversionItem,
    DividendItem,
    TaxItem,
    IssuanceFeeItem,
    CorporateActionItem,
    StockSplitItem,
]
