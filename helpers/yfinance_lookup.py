import yfinance as yf

top_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "BRK-B", "JNJ", "V",
    "UNH", "XOM", "JPM", "MA", "PG",
    "HD", "LLY", "PEP", "BAC", "COST"
]

def get_top_stock_info():
    results = []
    for symbol in top_tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            results.append({
                "symbol": symbol,
                "company_name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown")
            })
        except Exception:
            results.append({
                "symbol": symbol,
                "company_name": symbol,
                "sector": "Unknown"
            })
    return results
