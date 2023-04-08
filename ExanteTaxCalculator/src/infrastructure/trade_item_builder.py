from typing import Union, Optional, List
from money import Money

from src.domain.transactions import *
from src.domain.currency import Currency
from src.domain.share import Share

from src.infrastructure.report_row import ReportRow
from src.infrastructure.transaction_item_data import TransactionItemData
from src.infrastructure.errors import InvalidTradeError, InvalidReportRowError
from src.infrastructure.builders.building import build_autoconversions, is_money


class TradeItemBuilder:
    """
    TradeItemBuilder recognizes and builds specific TransactionItem based on received ReportRows.
    """

    def __init__(self) -> None:
        self._item = TransactionItemData()

    def add(self, row: ReportRow):
        self._item.add_row(row)
        return self

    def build(self) -> TransactionItem:
        inc = self._item.increase
        dec = self._item.decrease

        # transaction recognition is below
        result: TransactionItem

        if is_corporate_action(inc, dec):
            result = self._build_corporate_action_item()
        elif is_stock_split(inc, dec):
            result = self._build_stock_split_item()
        elif is_dividend(inc):
            result = self._build_dividend_item()
        elif is_tax(dec):
            result = self._build_tax_item(dec[0])
        elif is_issuance_fee(dec):
            result = self._build_issuance_fee_item(dec[0])
        # elif is_autoconversion(inc, dec):
        #     result = self._build_autoconversion_item()
        elif is_funding(inc, dec):
            result = self._build_funding_item()
        elif is_withdrawal(inc, dec):
            result = self._build_withdrawal_item()
        # decrease money and increase money -> exchange
        elif is_trade(inc) and is_money(inc) and len(dec) == 1 and is_trade(dec[0]) and is_money(dec[0]):
            result = self._build_exchange_item()
        # decrease money and increase asset -> buy
        elif is_trade(inc) and not is_money(inc) and len(dec) == 1 and is_trade(dec[0]) and is_money(dec[0]):
            result = self._build_buy_item()
        # increase money and decrease asset -> sell
        elif is_trade(inc) and is_money(inc) and len(dec) == 1 and is_trade(dec[0]) and not is_money(dec[0]):
            result = self._build_sell_item()
        elif is_autoconversion(self._item.autoconversions):
            result = self._build_autoconversion_item()
        else:
            raise InvalidTradeError(f"Unrecognized operation type:\ninc: {inc}\ndec: {dec}\nitem: {self._item}")

        self._item.reset()
        return result

    def _build_buy_item(self) -> BuyItem:
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        commission = self._item.commission
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        paid = -Money(dec.sum, dec.asset)
        commision = Money("0", dec.asset) if commission is None else -Money(commission.sum, commission.asset)
        autoconversions = build_autoconversions(self._item.autoconversions)

        return BuyItem(
            asset_name=inc.asset,
            amount=inc.sum,
            paid=paid,
            commission=commision,
            date=inc.when,
            transaction_id=transaction_id,
            autoconversions=autoconversions,
        )

    def _build_sell_item(self) -> SellItem:
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        commission = self._item.commission
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        received = Money(inc.sum, inc.asset)
        commission = Money("0", inc.asset) if commission is None else -Money(commission.sum, commission.asset)
        autoconversions = build_autoconversions(self._item.autoconversions)

        return SellItem(
            asset_name=dec.asset,
            amount=-dec.sum,
            received=received,
            commission=commission,
            autoconversions=autoconversions,
            date=dec.when,
            transaction_id=transaction_id,
        )

    def _build_funding_item(self) -> FundingItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for funding: {commission}")
        inc = self._item.increase
        assert inc is not None
        if not is_money(inc):
            raise InvalidTradeError(f"Tried funding with non-money: {inc}")
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return FundingItem(funding_amount=Money(inc.sum, inc.asset), date=inc.when, transaction_id=transaction_id)

    def _build_withdrawal_item(self) -> WithdrawalItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for withdrawal: {commission}")
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        if not is_money(dec):
            raise InvalidTradeError(f"Tried withdrawal with non-money: {dec}")
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return WithdrawalItem(-Money(dec.sum, dec.asset), dec.when, transaction_id)

    def _build_exchange_item(self) -> ExchangeItem:
        """Money exchange is stored under TRADE item"""
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for exchange: {commission}")
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        return ExchangeItem(
            exchange_from=-Money(dec.sum, dec.asset),
            exchange_to=Money(inc.sum, inc.asset),
            date=dec.when,
            transaction_id=transaction_id,
        )

    def _build_dividend_item(self) -> DividendItem:
        """Dividend has required dividend part and optional tax part"""
        inc = self._item.increase
        assert inc is not None
        dec = self._item.decrease
        transaction_id = self._item.transaction_id
        autoconversions = build_autoconversions(self._item.autoconversions)
        assert inc is not None
        assert transaction_id is not None
        # tax may be none; not reported together with dividend
        # issuance fee may be none; not reported together with dividend
        # there can be both: tax and issuance fee. Face that...

        if len(dec) > 2:
            raise InvalidTradeError(f"Dividend can have at most 2 money stealers (Tax, Issuance Fee), but got: {dec}")

        tax = issuance_fee = None
        for dec_item in dec:
            if dec_item.operation_type == ReportRow.OperationType.TAX:
                tax = self._build_tax_item(dec_item)
            elif dec_item.operation_type == ReportRow.OperationType.ISSUANCE_FEE:
                issuance_fee = self._build_issuance_fee_item(dec_item)
            else:
                raise InvalidTradeError(f"Dividend allowed money stealers are (Tax, Issuance Fee), but got: {dec_item}")

        dividend = Money(inc.sum, inc.asset)
        return DividendItem(
            received_dividend=dividend,
            paid_tax=tax,
            paid_issuance_fee=issuance_fee,
            autoconversions=autoconversions,
            date=inc.when,
            transaction_id=transaction_id,
            comment=inc.comment,
        )

    def _build_tax_item(self, dec: ReportRow) -> TaxItem:
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return TaxItem(paid_tax=-Money(dec.sum, dec.asset), date=dec.when, transaction_id=transaction_id, comment=dec.comment)

    def _build_issuance_fee_item(self, dec: ReportRow) -> IssuanceFeeItem:
        transaction_id = self._item.transaction_id
        assert transaction_id is not None
        return IssuanceFeeItem(paid_fee=-Money(dec.sum, dec.asset), date=dec.when, transaction_id=transaction_id, comment=dec.comment)

    def _build_autoconversion_item(self) -> AutoConversionItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for autoconversion: {commission}")
        inc = self._item.autoconversions[0].increase
        dec = self._item.autoconversions[0].decrease[0]  # len==1 checked during operation classification
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None
        return AutoConversionItem(
            conversion_from=-Money(dec.sum, dec.asset),
            conversion_to=Money(inc.sum, inc.asset),
            date=dec.when,
            transaction_id=transaction_id,
        )

    def _build_corporate_action_item(self) -> CorporateActionItem:
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None

        from_share = Share(amount=-dec.sum, symbol=dec.asset)
        to_share = Share(amount=inc.sum, symbol=inc.asset)
        return CorporateActionItem(from_share=from_share, to_share=to_share, date=dec.when, transaction_id=transaction_id)

    def _build_stock_split_item(self) -> StockSplitItem:
        inc = self._item.increase
        dec = self._item.decrease[0]  # len==1 checked during operation classification
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert transaction_id is not None

        from_share = Share(amount=-dec.sum, symbol=dec.asset)
        to_share = Share(amount=inc.sum, symbol=inc.asset)
        return StockSplitItem(from_share=from_share, to_share=to_share, date=dec.when, transaction_id=transaction_id)


def is_funding(inc: Optional[ReportRow], dec: List[ReportRow]) -> bool:
    return inc is not None and inc.operation_type == ReportRow.OperationType.FUNDING_WITHDRAWAL and len(dec) == 0


def is_withdrawal(inc: Optional[ReportRow], dec: List[ReportRow]) -> bool:
    return len(dec) == 1 and dec[0].operation_type == ReportRow.OperationType.FUNDING_WITHDRAWAL and inc is None


def is_trade(row: Optional[ReportRow]) -> bool:
    return row is not None and row.operation_type == ReportRow.OperationType.TRADE


def is_autoconversion(autoconversions: List[TransactionItemData]) -> bool:
    return len(autoconversions) > 0


def is_dividend(row: Optional[ReportRow]) -> bool:
    return row is not None and row.operation_type == ReportRow.OperationType.DIVIDEND


def is_tax(dec: List[ReportRow]) -> bool:
    return len(dec) == 1 and dec[0].operation_type == ReportRow.OperationType.TAX


def is_issuance_fee(dec: List[ReportRow]) -> bool:
    return len(dec) == 1 and dec[0].operation_type == ReportRow.OperationType.ISSUANCE_FEE


def is_corporate_action(inc: Optional[ReportRow], dec: List[ReportRow]) -> bool:
    return (
        inc is not None
        and inc.operation_type == ReportRow.OperationType.CORPORATE_ACTION
        and len(dec) == 1
        and dec[0].operation_type == ReportRow.OperationType.CORPORATE_ACTION
    )


def is_stock_split(inc: Optional[ReportRow], dec: List[ReportRow]) -> bool:
    return (
        inc is not None
        and inc.operation_type == ReportRow.OperationType.STOCK_SPLIT
        and len(dec) == 1
        and dec[0].operation_type == ReportRow.OperationType.STOCK_SPLIT
    )
