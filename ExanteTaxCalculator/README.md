# Exante broker stocks tax calculator for polish tax declaration

## Calculation rules

Rules by <https://jakoszczedzacpieniadze.pl/jak-rozliczyc-podatek-od-dywidendy-zagranicznej-i-zysk-na-akcjach-jaki-pit>:

- There is 19% tax to be collected from stocks income
- It is calculated in PLN, so need to convert USD->PLN for both buy and sell
- Quotation from previous working day should be used for buy and sell
- Profit is calculated in FIFO manner, eg.
  - Buy  (10 x 100USD - commission), convert to PLN by quotations from prev working day
  - Buy  (10 x 150USD - commission), convert to PLN by quotations from prev working day
  - Sell (15 x 200USD - commission), convert to PLN by quotations from prev working day
  - Income = (15 x 200USD) in PLN
  - Cost = (10 x 100USD) in PLN + (5 x 150USD) in PLN

## Exante data

```
Transaction ID  Account ID	  Symbol ID       Operation type      When                  Sum       Asset     EUR equivalent
61955151        TBA0174.001	  None            FUNDING/WITHDRAWAL  2020-06-23 14:41:21   13400     EUR       13400

62088337        TBA0174.001	  EUR/USD.EXANTE  TRADE               2020-06-24 19:52:01   -13400    EUR       -13400
62088340        TBA0174.001	  EUR/USD.EXANTE  TRADE               2020-06-24 19:52:01   15067.63  USD       13386.73

62088984        TBA0174.001	  SHY.ARCA	      TRADE               2020-06-24 19:54:08   150       SHY.ARCA  11534.16    // buy/sell subject
62088986        TBA0174.001	  SHY.ARCA	      TRADE               2020-06-24 19:54:08   -12985.5  USD       -11534.16   // paid/received money
62088988        TBA0174.001	  SHY.ARCA	      COMMISSION          2020-06-24 19:54:08   -3        USD       -2.66       // paid commission (optional)

62368140        TBA0174.001   SHY.ARCA        TRADE               2020-06-29 16:07:33   -70       SHY.ARCA  -5395.76
62368141        TBA0174.001   SHY.ARCA        TRADE               2020-06-29 16:07:33   6062      USD       5395.76
62368142        TBA0174.001   SHY.ARCA        COMMISSION          2020-06-29 16:07:33   -1.4      USD       -1.25
```

??? should currency exchange eur->usd, then usd->eur be subject to 19% tax???

Operations:
- Funding: (Currency, Amount, date)
- Withdrawal: (Currency, Amount, date)
- Currency exchange: (From Currency, From decrease, To Currency, To increase)
- Buy - (Asset amount, Asset name, PaidCurrency, PaidAmount, CommisionCurrency, CommissionAmount, Date)
- Sell - (Asset amount, Asset name, PaidCurrency, PaidAmount, CommisionCurrency, CommissionAmount, Date) - here is the FIFO logic, partial commision etc

Rules:
- cant withdraw curency if no enough currency
- cant exchange currency if no enough FROM currency
- cant buy asset if no enough currency
- cant sell asset if no enough of that asset

## Testing

MoneyPayedIn(currency, amount, date)
MoneyWithdrawn(currency, amount, date)
StocksBought(name, amount, price, date, commission)
StocksSold(name, amount, price, date, commission)

repo.Add(GDXJ, +100, 5.0,  10.01.2020)
repo.Add(comm,   -1, 1.0,  10.01.2020)
repo.Add(GDXJ, +100, 10.0, 20.01.2020)
repo.Add(comm,   -1, 1.0,  20.01.2020)
repo.Add(GDXJ, -150, 20.0  30.01.2020)
repo.Add(comm,   -1, 1.0,  30.01.2020)

calc.Fund(100, EUR, 01.10.2020)
calc.Exchange(100, EUR, 120, USD, 01.10.2020)
calc.Buy(10, PHYS, 100, USD, 1, USD, 10.10.2020)
calc.Buy(10, PHYS, 200, USD, 1, USD, 20.10.2020)
calc.Sel(15, PHYS, 300, USD, 1, USD, 30.10.2020)
calc.Withdraw(50, EUR, 01.11.2020)

resultMap = calc.Get(2020)
physResult = resultMap[phys]