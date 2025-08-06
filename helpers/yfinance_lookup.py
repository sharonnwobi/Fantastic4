import yfinance as yf


def get_stock_info(symbol):
    stock = yf.Ticker(symbol)

    try:
        info = stock.info
        history = stock.history(period="1d", interval="5m")
    except Exception as e:
        return f"Error fetching stock data: {e}", 500

    timestamps = history.index.strftime('%H:%M').tolist()
    prices = history["Close"].fillna(method="ffill").tolist()
    
    return {
        "info": info,
        "timestamps": timestamps,
        "prices": prices
    }
    
def get_stock_current_price(symbol):
    stock = yf.Ticker(symbol)
    try:
        current_price = stock.history(period="1d").iloc[-1]["Close"]
    except Exception as e:
        return f"Error fetching current price: {e}", 500
    return current_price