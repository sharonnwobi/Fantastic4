import yfinance as yf

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1m")
    times = data.index.strftime('%Y-%m-%d %H:%M:%S')
    average_prices = (data['Open'] + data['Close']) / 2
    volume = data['Volume']
    return times.tolist(), average_prices.tolist()

print(get_stock_data("AAPL")) 