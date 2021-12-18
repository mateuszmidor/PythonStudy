from dataclasses import dataclass


@dataclass(frozen=True)
class StockExchange:
    country: str  # Wielka Brytania
    name: str  # London Stock Exchange
    short: str  # LSE


known_stock_exchanges = [
    StockExchange("Stany Zjednoczone", "American Stock Exchange NYSE", "AMEX"),
    StockExchange("Stany Zjednoczone", "Archipelago Exchange NYSE", "ARCA"),
    StockExchange("Grecja", "Athens Stock Exchange", "ASE"),
    StockExchange("Australia", "Australian Securities Exchange", "ASX"),
    StockExchange("Stany Zjednoczone", "BATS Global Markets", "BATS"),
    StockExchange("Turcja", "Borsa İstanbul", "BIST"),
    StockExchange("Dania", "Copenhagen Stock Exchange", "OMXC"),
    StockExchange("Finlandia", "Helsinki Stock Exchange", "OMXH"),
    StockExchange("Chiny", "Hong Kong Exchanges and Clearing Limited", "HKEX"),
    StockExchange("RPA", "Johannesburg Stock Exchange", "JSE"),
    StockExchange("Wielka Brytania", "London Stock Exchange", "LSE"),
    StockExchange("Wielka Brytania", "London Stock Exchange Alternative Investment Market", "LSEAIM"),
    StockExchange("Wielka Brytania", "London Stock Exchange International Order Book", "LSEIOB"),
    StockExchange("Hiszpania", "Madrid Stock Exchange", "BM"),
    StockExchange("Malta", "Malta Stock Exchange", "MSE"),
    StockExchange("Rosja", "Moscow Exchange", "MOEX"),
    StockExchange("Norwegia", "NASDAQ OMX Oslo NASDAQ", "OMX"),
    StockExchange("Stany Zjednoczone", "Nasdaq Stock Market", "NASDAQ"),
    StockExchange("Stany Zjednoczone", "New York Stock Exchange", "NYSE"),
    StockExchange("Szwecja", "Nordic OMX", "NOMX"),
    StockExchange("Norwegia", "Oslo Stock Exchange", "OSE"),
    StockExchange("Stany Zjednoczone", "OTC Bulletin Board", "OTCBB"),
    StockExchange("Stany Zjednoczone", "OTC Markets Group", "OTCMKTS"),
    StockExchange("Republika Czeska", "Prague Stock Exchange", "PSE"),
    StockExchange("Singapur", "Singapore Exchange", "SGX"),
    StockExchange("Szwecja", "Stockholm Stock Exchange", "SOMX"),
    StockExchange("Szwajcaria", "Swiss Exchange", "SIX"),
    StockExchange("Izrael", "Tel-Aviv Stock Exchange", "TASE"),
    StockExchange("Japonia", "Tokyo Stock Exchange", "TSE"),
    StockExchange("Kanada", "Toronto Stock Exchange", "TMX"),
    StockExchange("Austria", "Vienna Stock Exchange", "VSE"),
    StockExchange("Polska", "Warsaw Stock Exchange", "WSE"),
    StockExchange("Niemcy", "Xetra Stock Exchange", "XETRA"),
    # EURONEXT is problematic; how to decide country when short is the same for a number of countries?
    # StockExchange("Włochy", "Borsa Italiana", "EURONEXT"),
    # StockExchange("Holandia", "Euronext Amsterdam", "EURONEXT"),
    # StockExchange("Belgia", "Euronext Brussels", "EURONEXT"),
    # StockExchange("Irlandia", "Euronext Ireland", "EURONEXT"),
    # StockExchange("Portugalia", "Euronext Lisbon", "EURONEXT"),
    # StockExchange("Francja", "Euronext Paris", "EURONEXT"),
]


def stock_exchange_by_short_name(short_name: str) -> StockExchange:
    for stock_exchange in known_stock_exchanges:
        if stock_exchange.short == short_name:
            return stock_exchange
    raise ValueError(f"Unknown stock exchange: '{short_name}'")
