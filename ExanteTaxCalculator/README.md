# Exante trading tax calculator for polish tax declaration

## Calculation rules

Rules by <https://jakoszczedzacpieniadze.pl/jak-rozliczyc-podatek-od-dywidendy-zagranicznej-i-zysk-na-akcjach-jaki-pit>:

- There is 19% tax to be collected from item sell income (only when sell was profitable)
- There is 19% tax to be collected from dividend income, not all but most most dividends are auto-taxed 15% so need calc and  pay additional 4%
- It is calculated in PLN, so need to convert trade currency->PLN for all: buy, sell, dividend, tax
- Quotation average by NBP from previous working day should be used for buy and sell, dividend and tax
- Profit for sell items is calculated in FIFO manner, eg.
  - Buy  (10 x 100USD - commission), convert to PLN using quotations from prev working day
  - Buy  (5  x 150USD - commission), convert to PLN using quotations from prev working day
  - Sell (15 x 200USD - commission), convert to PLN using quotations from prev working day
  - Income = (15 x 200USD - commission) in PLN
  - Cost = (10 x 100USD + commission) in PLN + (5 x 150USD + commission) in PLN

## TODO

- rename asset to share (assets in wallet = currencies + shares)
[OK] - rename TaxableItem -> BuySellPair
[OK]- rename TaxableItemPLN -> BuySellPairPLN
[OK] - rename Trader -> BuySellMatcher
[OK] - make TradesRepoCSV return items sorted by date ascending so Wallet doesnt protest with insufficient funds
[OK] - make AssetWallet to track all buy/sell/fund/withdraw/exchange operations and validate for sufficient funds
[OK] - add support for CORPORATE ACTION
[OK] - add support for DIVIDEND
[OK] - add support for TAX
[OK] - add support for AUTOCONVERSION
[OK] - complement TaxCalculator with Dividend and Tax support
- add report printer - where did profits and taxes come from
- add selecting year to calc the profits and taxes for
- make ProfitItem independend from the BuySellIPairPLN -> BuySellPair -> BuyItem & SellItem

## Exante data

```
Transaction ID  Account ID	  Symbol ID       Operation type      When                  Sum       Asset     EUR equivalent  Comment
61955151        TBA0174.001	  None            FUNDING/WITHDRAWAL  2020-06-23 14:41:21   13400     EUR       13400

62088337        TBA0174.001	  EUR/USD.EXANTE  TRADE               2020-06-24 19:52:01   -13400    EUR       -13400
62088340        TBA0174.001	  EUR/USD.EXANTE  TRADE               2020-06-24 19:52:01   15067.63  USD       13386.73

62088984        TBA0174.001	  SHY.ARCA	      TRADE               2020-06-24 19:54:08   150       SHY.ARCA  11534.16    // buy/sell subject
62088986        TBA0174.001	  SHY.ARCA	      TRADE               2020-06-24 19:54:08   -12985.5  USD       -11534.16   // paid/received money
62088988        TBA0174.001	  SHY.ARCA	      COMMISSION          2020-06-24 19:54:08   -3        USD       -2.66       // paid commission (optional)

62368140        TBA0174.001   SHY.ARCA        TRADE               2020-06-29 16:07:33   -70       SHY.ARCA  -5395.76
62368141        TBA0174.001   SHY.ARCA        TRADE               2020-06-29 16:07:33   6062      USD       5395.76
62368142        TBA0174.001   SHY.ARCA        COMMISSION          2020-06-29 16:07:33   -1.4      USD       -1.25

72637626        TBA0174.001   IEF.ARCA        CORPORATE ACTION    2020-10-27 16:36:04   -20	      IEF.ARCA	 -2027.87       IEF.ARCA to IEF.NASDAQ
72637631        TBA0174.001   IEF.NASDAQ      CORPORATE ACTION    2020-10-27 16:36:04   20        IEF.NASDAQ	2063.21       IEF.ARCA to IEF.NASDAQ

77471454        TBA0174.001   CLR.SGX         AUTOCONVERSION      2020-12-08 06:27:21   2.5       SGD        1.54
77471455        TBA0174.001   CLR.SGX         AUTOCONVERSION      2020-12-08 06:27:21   -1.88     USD        -1.55

78757917        TBA0174.001   IEF.NASDAQ      DIVIDEND            2020-12-17 11:02:25   1.45      USD        1.19	20.0 shares 2020-12-17 dividend IEF.NASDAQ 1.45 USD (0.072535 per share) tax 0.22 USD (15.0%)
78757918        TBA0174.001   IEF.NASDAQ      TAX                 2020-12-17 11:02:25   -0.22     USD        -0.18	None
```

Note: usually TAX follows DIVIDEND, buy sometimes:
- TAX is reported much later with comment pointing to DIVIDEND TransactionID
- TAX is not reported AT ALL

??? should currency exchange eur->usd, then usd->eur be subject to 19% tax???

Operations:
  - "TRADE"
  - "COMMISSION"
  - "FUNDING/WITHDRAWAL"
  - "AUTOCONVERSION"
  - "DIVIDEND"
  - "TAX"
  - "CORPORATE ACTION"

AutoConversion - like currency exchange but OperationType is AUTOCONVERSION instead of TRADE
    NOTICE: Autoconversion is triggered automatically by other kind of operation that needs money, eg
    in case of trade there can be autoconversino to cover the shares cost and another autoconversion for the commission

Rules:
- cant withdraw curency if no enough currency
- cant exchange currency if no enough FROM currency
- cant buy asset if no enough currency
- cant sell asset if no enough of that asset


BuySellProfitLoss = profits(loses) from buy-sell items
DividendProfit = profit from dividend items
TotalProfit = BuySellProfitLoss + DividendProfit
TotalTaxDue = 19% * TotalProfit
TaxAlreadyPayed = tax from Dividends(15%) + Freestanding taxes(probably also from dividends but delayed)
TaxToPay = TotalTaxDue - TaxAlreadyPayed, includes BuySell 19% taxes and 4% complement tax for dividends
ToWithdrawAndParty = TotalProfit - TaxToPay

### more like a code

1. Collect BuySellItems, DividendItems, TaxItems
2. Quote the above and receive BuySellItemsPLN, DividendItemsPLN, TaxItemsPLN
3. from BuySellItemsPLN calc ProtifItemsPLN

# tax calculator
TotalProfit = sum(ProfitItemsPLN) + sum(DividendItemsPLN)
TotalTaxDue = 19% * TotalProfit
TaxAlreadyPayed = sum(TaItemsPLN)
TaxToPay = TotalTaxDue - TaxAlreadyPayed, includes BuySell 19% taxes and 4% complement tax for dividends

# for fun
ToWithdrawAndParty = TotalProfit - TaxToPay