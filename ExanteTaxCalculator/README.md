# Exante trading tax calculator for polish tax declaration

## Requirements

- python3, pip3

## Install

```bash
pip install .
```

## Run

```bash
exante-calculator exante_report.csv 2020 
```

## Development

Run tests:
```bash
./run_all --test
```

Run command:
```bash
./run_all data/exante_report.csv 2020
```

## Input needed for tax declaration

- total income = sum of money from sells + sum of money from dividends ("Przychód")
- total cost = sum of money paid for buys that are paired with sells ("Koszty uzyskania przychodu")
- net profit = total cost - total income ("Dochód")
- previus years loss ("Strata z lat ubiegłych")
- tax base = net profit - previus years loss ("Podstawa obliczenia podatku")
- total tax = 19% * tax base ("Podatek od dochodów")
- tax already paid ("Podatek zapłacony za granicą")
- tax yet to pay = max(total tax - tax already paid, 0) ("Podatek należny")

## Calculation rules

Rules by <https://jakoszczedzacpieniadze.pl/jak-rozliczyc-podatek-od-dywidendy-zagranicznej-i-zysk-na-akcjach-jaki-pit>:

- There is 19% tax to be collected from item sell income (only when sell was profitable)
- There is 19% tax to be collected from dividend income, not all but most most dividends are auto-taxed 15% so need calc and pay additional 4%.
(US seems to claim 4% regardless how much you actually already paid 15% (with W-8BEN signed) or 30%, though. Should always pay 4% of received dividends sum?)
- Tax is calculated in PLN, so need to convert trade currency->PLN for all: buy, sell, dividend, tax
- Quotation average by NBP from previous working day should be used for buy and sell, dividend and tax (so called D-1 day)
- Profit for sell items is calculated in FIFO manner, eg.
  - Buy  (10 x 100USD - commission), convert to PLN using quotations from prev working day
  - Buy  (5  x 150USD - commission), convert to PLN using quotations from prev working day
  - Sell (15 x 200USD - commission), convert to PLN using quotations from prev working day
  - Income = (15 x 200USD - commission) in PLN
  - Cost = (10 x 100USD + commission) in PLN + (5 x 150USD + commission) in PLN
- Shares sell income and dividend income are calculated separately into separate fields in tax declaration

## Algorithm

- parse transaction history CSV into dedicated structures and sort by date from old to new
- match sell transactions with buy transactions in FIFO manner, remembering how many shares were sold in this specific Buy/Sell pair
- quote all the Buy/Sell pairs in PLN (NBP quotation: take previous working day from sell date)
- quote all Dividends in PLN
- quote all Taxes in PLN
- calc income and cost of every Buy/Sell pair and store into Profit ite. Amounts depend on how many shares were sold in each specific pair;  
  buy commission increases the cost part and sell commission decreases the income part
- calc total income as sum of sells and dividends
- calc total cost as sum of all buys
- calc tax already paid as sum of all taxes
- calc profit as total income - total cost
- calc tax as max(profit, 0) * 19%
- calc tax to pay as max(tax - tax alread paid, 0)

## TODO

- [OK] - rename TaxableItem -> BuySellPair
- [OK] - rename TaxableItemPLN -> BuySellPairPLN
- [OK] - rename Trader -> BuySellMatcher
- [OK] - make TradesRepoCSV return items sorted by date ascending so Wallet doesnt protest with insufficient funds
- [OK] - make AssetWallet to track all buy/sell/fund/withdraw/exchange operations and validate for sufficient funds
- [OK] - add support for CORPORATE ACTION
- [OK] - add support for DIVIDEND
- [OK] - add support for TAX
- [OK] - add support for AUTOCONVERSION
- [OK] - complement TaxDeclarationNumbersCalculator with Dividend and Tax support
- [OK] - add report printer - where did profits and taxes come from
- [OK] - group report transactions per asset and include summary: income, cost, profit
- [OK] - separate profit & tax for dividends; they live in separate field in tax declaration
- rename asset to share (assets in wallet = currencies + shares)
- add selecting year to calc the profits and taxes for
- improvement: make ProfitItem independend from the BuySellIPairPLN -> BuySellPair -> BuyItem & SellItem

## Exante data

Notice: 
- transactions exported from Exante are sorted by date descending. So start reading from the bottom
- transactions building single trade have same date and time, and TransactionID incrementing

```
Transaction ID  Account ID    Symbol ID       Operation type      When                  Sum       Asset     EUR equivalent  Comment

78757917        TBA0174.001   IEF.NASDAQ      DIVIDEND            2020-12-17 11:02:25   1.45      USD        1.19           20.0 shares 2020-12-17 dividend IEF.NASDAQ 1.45 USD (0.072535 per share) tax 0.22 USD (15.0%)
78757918        TBA0174.001   IEF.NASDAQ      TAX                 2020-12-17 11:02:25   -0.22     USD        -0.18  

77471454        TBA0174.001   CLR.SGX         AUTOCONVERSION      2020-12-08 06:27:21   2.5       SGD        1.54
77471455        TBA0174.001   CLR.SGX         AUTOCONVERSION      2020-12-08 06:27:21   -1.88     USD        -1.55

72637626        TBA0174.001   IEF.ARCA        CORPORATE ACTION    2020-10-27 16:36:04   -20       IEF.ARCA   -2027.87       IEF.ARCA to IEF.NASDAQ
72637631        TBA0174.001   IEF.NASDAQ      CORPORATE ACTION    2020-10-27 16:36:04   20        IEF.NASDAQ  2063.21       IEF.ARCA to IEF.NASDAQ

62368140        TBA0174.001   SHY.ARCA        TRADE               2020-06-29 16:07:33   -70       SHY.ARCA  -5395.76
62368141        TBA0174.001   SHY.ARCA        TRADE               2020-06-29 16:07:33   6062      USD       5395.76
62368142        TBA0174.001   SHY.ARCA        COMMISSION          2020-06-29 16:07:33   -1.4      USD       -1.25

62088984        TBA0174.001   SHY.ARCA        TRADE               2020-06-24 19:54:08   150       SHY.ARCA  11534.16        // buy/sell subject
62088986        TBA0174.001   SHY.ARCA        TRADE               2020-06-24 19:54:08   -12985.5  USD       -11534.16       // paid/received money
62088988        TBA0174.001   SHY.ARCA        COMMISSION          2020-06-24 19:54:08   -3        USD       -2.66           // paid commission 

62088337        TBA0174.001   EUR/USD.EXANTE  TRADE               2020-06-24 19:52:01   -13400    EUR       -13400
62088340        TBA0174.001   EUR/USD.EXANTE  TRADE               2020-06-24 19:52:01   15067.63  USD       13386.73

61955151        TBA0174.001   None            FUNDING/WITHDRAWAL  2020-06-23 14:41:21   13400     EUR       13400
```

Note: usually DIVIDEND is followed by TAX, buy sometimes:
- TAX is reported much later with comment pointing to DIVIDEND TransactionID
- TAX is not reported at all - mostlikely not deducted

Questions:
- should currency exchange pln->usd, then usd->pln be subject to 19% tax???
- if so, what happens in case of scenario:
  1. PLN/USD is 3
  1.  exchange 3000 PLN -> 1000 USD
  1.  buy shares for 1000 USD
  1.  PLN/USD grows from 3 to 4
  1.  sell shares for 1000 USD. Profit = 4000 PLN - 3000 PLN = 1000 PLN, Tax 190PLN
  1.  exchange 1000 USD -> 4000 PLN. Profit = 4000 PLN - 3000 PLN = 1000 PLN, AGAIN Tax 190PLN?

Operations listed in report:
  - "FUNDING/WITHDRAWAL"
  - "TRADE" (covers money exchange)
  - "COMMISSION" (optional, no commission in case of exchange)
  - "AUTOCONVERSION"
  - "DIVIDEND"
  - "TAX"
  - "CORPORATE ACTION"

Glossary:
- money - currency with 3 characters symbol like USD, CAD, EUR
- share - you buy it for money, many characters symbol like SHY.ARCA
- asset - money or shares, reported in column "Asset"

Operations on wallet:
- funding - add money to wallet
- withdrawal - remove money from wallet
- exchange - exchange of money; one currency for another
- autoconversion - automatically exchange one currency for another (happens with buy when needed currency is not in wallet or for dividends)
- buy - buy shares for money
- sell - sell shares for money
- corporate action - rename shares
- dividend - add money, optionally also add tax
- tax - add tax

AutoConversion - like currency exchange but OperationType is AUTOCONVERSION instead of TRADE
    NOTICE: Autoconversion is triggered automatically by other kind of operation: Buy, Sell, Dividend, eg
    in case of trade there can be autoconversion to cover the shares cost and another autoconversion for the commission


## CRYPTO

- can't collectively calc tax from crypto and other investments
- separate place on declaration to testify crypto cost and profit  
- crypto exchange for another crypto is not subject to tax, only sell for real money

