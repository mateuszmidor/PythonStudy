from typing import Union, Optional, List
from money import Money

from src.domain.transactions import *
from src.domain.currency import Currency
from src.domain.share import Share

from src.infrastructure.report_row import ReportRow
from src.infrastructure.transaction_item_data import TransactionItemData
from src.infrastructure.errors import InvalidTradeError, InvalidReportRowError


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
        elif inc is not None and is_dividend(inc):
            result = self._build_dividend_item()
        elif is_tax(dec):
            result = self._build_tax_item()
        elif is_autoconversion(inc, dec):
            result = self._build_autoconversion_item()
        elif is_funding(inc, dec):
            result = self._build_funding_item()
        elif is_withdrawal(inc, dec):
            result = self._build_withdrawal_item()
        # decrease money and increase money -> exchange
        elif is_trade(inc) and is_money(inc) and is_trade(dec) and is_money(dec):
            result = self._build_exchange_item()
        # decrease money and increase asset -> buy
        elif is_trade(inc) and not is_money(inc) and is_trade(dec) and is_money(dec):
            result = self._build_buy_item()
        # increase money and decrease asset -> sell
        elif is_trade(inc) and is_money(inc) and is_trade(dec) and not is_money(dec):
            result = self._build_sell_item()
        # increase asset and decrease asset -> barter trade
        elif not is_money(inc) and not is_money(dec):
            raise InvalidTradeError(f"Both assets are non-money -> barter trade not suported: {inc}, {dec}")
        else:
            raise InvalidTradeError("Trade type is other than: buy/sell/fund/withdraw/exchange/autoconversion/dividend/tax/corporate action")

        self._item.reset()
        return result

    def _build_buy_item(self) -> BuyItem:
        inc = self._item.increase
        dec = self._item.decrease
        commission = self._item.commission
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert dec is not None
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
        dec = self._item.decrease
        commission = self._item.commission
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert dec is not None
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
        dec = self._item.decrease
        if not is_money(dec):
            raise InvalidTradeError(f"Tried withdrawal with non-money: {dec}")
        transaction_id = self._item.transaction_id
        assert dec is not None
        assert transaction_id is not None
        return WithdrawalItem(-Money(dec.sum, dec.asset), dec.when, transaction_id)

    def _build_exchange_item(self) -> ExchangeItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for exchange: {commission}")
        inc = self._item.increase
        dec = self._item.decrease
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert dec is not None
        assert transaction_id is not None
        return ExchangeItem(
            exchange_from=-Money(dec.sum, dec.asset),
            exchange_to=Money(inc.sum, inc.asset),
            date=dec.when,
            transaction_id=transaction_id,
        )

    def _build_dividend_item(self) -> DividendItem:
        """ Dividend has required dividend part and optional tax part """
        inc = self._item.increase
        assert inc is not None
        dec = self._item.decrease
        transaction_id = self._item.transaction_id
        autoconversions = build_autoconversions(self._item.autoconversions)
        assert inc is not None
        assert transaction_id is not None
        # tax may be none; not reported together with dividend
        if dec is not None and dec.operation_type != ReportRow.OperationType.TAX:
            raise InvalidTradeError(f"Unexpected operation type, expected TAX, got: {dec.operation_type}")
        dividend = Money(inc.sum, inc.asset)
        tax = self._build_tax_item() if dec is not None else None
        return DividendItem(
            received_dividend=dividend,
            paid_tax=tax,
            autoconversions=autoconversions,
            date=inc.when,
            transaction_id=transaction_id,
            comment=inc.comment,
        )

    def _build_tax_item(self) -> TaxItem:
        dec = self._item.decrease
        transaction_id = self._item.transaction_id
        assert dec is not None
        assert transaction_id is not None
        return TaxItem(paid_tax=-Money(dec.sum, dec.asset), date=dec.when, transaction_id=transaction_id, comment=dec.comment)

    def _build_autoconversion_item(self) -> AutoConversionItem:
        commission = self._item.commission
        if commission is not None:
            raise InvalidTradeError(f"Unexpected commission for autoconversion: {commission}")
        inc = self._item.increase
        dec = self._item.decrease
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert dec is not None
        assert transaction_id is not None
        return AutoConversionItem(
            conversion_from=-Money(dec.sum, dec.asset), conversion_to=Money(inc.sum, inc.asset), date=dec.when, transaction_id=transaction_id
        )

    def _build_corporate_action_item(self) -> CorporateActionItem:
        inc = self._item.increase
        dec = self._item.decrease
        transaction_id = self._item.transaction_id
        assert inc is not None
        assert dec is not None
        assert transaction_id is not None

        from_share = Share(amount=-dec.sum, symbol=dec.asset)
        to_share = Share(amount=inc.sum, symbol=inc.asset)
        return CorporateActionItem(from_share=from_share, to_share=to_share, date=dec.when, transaction_id=transaction_id)


def is_money(row: Optional[ReportRow]) -> bool:
    return row is not None and Currency.is_currency(row.asset)


def is_funding(inc, dec: Optional[ReportRow]) -> bool:
    return inc is not None and inc.operation_type == ReportRow.OperationType.FUNDING_WITHDRAWAL and dec is None


def is_withdrawal(inc, dec: Optional[ReportRow]) -> bool:
    return dec is not None and dec.operation_type == ReportRow.OperationType.FUNDING_WITHDRAWAL and inc is None


def is_trade(row: Optional[ReportRow]) -> bool:
    return row is not None and row.operation_type == ReportRow.OperationType.TRADE


def is_autoconversion(inc, dec: Optional[ReportRow]) -> bool:
    return (
        inc is not None
        and inc.operation_type == ReportRow.OperationType.AUTOCONVERSION
        and dec is not None
        and dec.operation_type == ReportRow.OperationType.AUTOCONVERSION
    )


def is_dividend(row: Optional[ReportRow]) -> bool:
    return row is not None and row.operation_type == ReportRow.OperationType.DIVIDEND


def is_tax(row: Optional[ReportRow]) -> bool:
    return row is not None and row.operation_type == ReportRow.OperationType.TAX


def is_corporate_action(row1, row2: Optional[ReportRow]) -> bool:
    return (
        row1 is not None
        and row1.operation_type == ReportRow.OperationType.CORPORATE_ACTION
        and row2 is not None
        and row2.operation_type == ReportRow.OperationType.CORPORATE_ACTION
    )


def build_autoconversions(items: List[TransactionItemData]) -> List[AutoConversionItem]:
    results: List[AutoConversionItem] = []
    for item in items:
        assert item.decrease is not None
        assert item.increase is not None
        assert item.transaction_id is not None
        result = AutoConversionItem(
            conversion_from=-Money(item.decrease.sum, item.decrease.asset),
            conversion_to=Money(item.increase.sum, item.increase.asset),
            date=item.increase.when,
            transaction_id=item.transaction_id,
        )
        results.append(result)
    return results
