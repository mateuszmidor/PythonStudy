import re
from datetime import datetime
from dataclasses import dataclass
from typing import List
import csv
from decimal import Decimal
from enum import Enum


# Below dataclass represents Money, which is used to represent amount of some currency
@dataclass
class Money:
    amount: Decimal
    currency: str


# Below class is used to represent Side of the trade
class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# Below dataclass represents Binance trade CSV table, which looks like this:
# Date(UTC),          Pair,  Side,Price,             Executed,       Amount,         Fee
# 2022-12-05 16:11:37,BTCEUR,BUY,"16,242.7900000000",0.0238600000BTC,387.55296940EUR,0.0000000000BNB
@dataclass
class BinanceTrade:
    date: datetime
    pair: str
    side: Side
    price: Decimal  # always positive number
    executed: Money  # always positive number
    amount: Money  # always positive number
    fee: Money  # positive or zero


# Below dataclass represents Exante CSV table, which looks like this:
# Transaction ID	Account ID	Symbol ID	ISIN	Operation type	When	Sum	Asset	EUR equivalent	Comment	UUID	Parent UUID
# 419613644	TBA0174.001	FXF.ARCA	None	COMMISSION	2022-12-07 14:50:45	-0.2	USD	-0.19	None	43fb135b-33df-4b87-94ce-cf4fbb5e8753	None
# 419613642	TBA0174.001	FXF.ARCA	None	TRADE	2022-12-07 14:50:45	950.5	USD	903.37	None	15e9b576-e96f-44c7-80a7-ff0b6705dd54	None
# 419613640	TBA0174.001	FXF.ARCA	US46138R1086	TRADE	2022-12-07 14:50:45	-10	FXF.ARCA	-903.37	None	9921f3d6-cf73-4daf-a821-4a620c2869d0	None

@dataclass
class ExanteRow:
    transaction_id: str
    account_id: str
    symbol_id: str
    isin: str
    operation_type: str
    when: datetime
    sum: Decimal
    asset: str
    eur_equivalent: Decimal
    comment: str
    uuid: str
    parent_uuid: str


# Below function takes list of ExanteRow and writies it to CSV file in following format
# Transaction ID	Account ID	Symbol ID	ISIN	Operation type	When	Sum	Asset	EUR equivalent	Comment	UUID	Parent UUID
# 419613644	TBA0174.001	FXF.ARCA	None	COMMISSION	2022-12-07 14:50:45	-0.2	USD	-0.19	None	43fb135b-33df-4b87-94ce-cf4fbb5e8753	None
# 419613642	TBA0174.001	FXF.ARCA	None	TRADE	2022-12-07 14:50:45	950.5	USD	903.37	None	15e9b576-e96f-44c7-80a7-ff0b6705dd54	None
# 419613640	TBA0174.001	FXF.ARCA	US46138R1086	TRADE	2022-12-07 14:50:45	-10	FXF.ARCA	-903.37	None	9921f3d6-cf73-4daf-a821-4a620c2869d0	None
def write_exante_csv(rows: List[ExanteRow], filename: str) -> None:
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter="\t", quotechar='"', quoting=csv.QUOTE_NONE)
        writer.writerow(
            [
                "Transaction ID",
                "Account ID",
                "Symbol ID",
                "ISIN",
                "Operation type",
                "When",
                "Sum",
                "Asset",
                "EUR equivalent",
                "Comment",
                "UUID",
                "Parent UUID",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.transaction_id,
                    row.account_id,
                    row.symbol_id,
                    row.isin,
                    row.operation_type,
                    row.when,
                    row.sum,
                    row.asset,
                    row.eur_equivalent,
                    row.comment,
                    row.uuid,
                    row.parent_uuid,
                ]
            )


# following function takes Trades as input and returns ExanteRows
def trade_to_exante_row(trades: List[BinanceTrade]) -> List[ExanteRow]:
    ACCOUNT_ID = "BINANCE"
    ISIN = "NONE"

    rows = []
    for transaction_id, trade in enumerate(reversed(trades)):
        if trade.side == Side.BUY:
            _from = trade.amount
            _to = trade.executed
        else:
            _from = trade.executed
            _to = trade.amount

        symbol = trade.executed.currency
        comment = f"generated from {trade}"

        # decrease
        rows.append(
            ExanteRow(
                transaction_id=str(transaction_id * 3 + 0),
                account_id=ACCOUNT_ID,
                symbol_id=symbol,
                isin=ISIN,
                operation_type="TRADE",
                when=trade.date,
                sum=-_from.amount,
                asset=_from.currency,
                eur_equivalent=Decimal(0),  # not known from Binance Report
                comment=comment,
                uuid="",
                parent_uuid="",
            )
        )

        # increase
        rows.append(
            ExanteRow(
                transaction_id=str(transaction_id * 3 + 1),
                account_id=ACCOUNT_ID,
                symbol_id=symbol,
                isin=ISIN,
                operation_type="TRADE",
                when=trade.date,
                sum=_to.amount,
                asset=_to.currency,
                eur_equivalent=Decimal(0),  # not known from Binance Report
                comment=comment,
                uuid="",
                parent_uuid="",
            )
        )

        # fee
        rows.append(
            ExanteRow(
                transaction_id=str(transaction_id * 3 + 2),
                account_id=ACCOUNT_ID,
                symbol_id=symbol,
                isin=ISIN,
                operation_type="COMMISSION",
                when=trade.date,
                sum=-trade.fee.amount,
                asset=trade.fee.currency,
                eur_equivalent=Decimal(0),  # not known from Binance Report
                comment=comment,
                uuid="",
                parent_uuid="",
            )
        )

    # reverse order - latest trades first
    rows = list(reversed(rows))
    return rows


# following function reads Binance Trades from CSV file
def read_binance_trades_csv(filename: str) -> List[BinanceTrade]:
    trades = []

    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        for row in reader:
            print(f"Processing: {row}")
            date = datetime.fromisoformat(row[0])
            pair = row[1]
            side = Side(row[2])
            price = Decimal(row[3])
            executed_amount, executed_currency = re.match(r"^([\d.]+)(\D+)$", row[4]).groups()
            amount_amount, amount_currency = re.match(r"^([\d.]+)(\D+)$", row[5]).groups()
            fee_amount, fee_currency = re.match(r"^([\d.]+)(\D+)$", row[6]).groups()
            executed = Money(amount=Decimal(executed_amount), currency=executed_currency)
            amount = Money(amount=Decimal(amount_amount), currency=amount_currency)
            fee = Money(amount=Decimal(fee_amount), currency=fee_currency)
            trades.append(BinanceTrade(date, pair, side, price, executed, amount, fee))

    # sort trades by date descending
    trades.sort(key=lambda x: x.date, reverse=True)
    return trades
