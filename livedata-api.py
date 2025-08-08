import yfinance as yf

period_intervals = {
    "1d":   "5m",    
    "5d":   "15m",   
    "1mo":  "30m",   
    "6mo":  "1d",  
    "ytd":  "1d",  
    "1y":   "1d", 
}

def get_stock_data(ticker, period="5d"): #to be changed to user input from front-end
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=period_intervals[period])

    times = data.index.strftime('%Y-%m-%d %H:%M:%S')
    volume = data['Volume']

    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    average_price = (typical_price * volume).cumsum() / volume.cumsum()

    graph_data = {
        "times": times.tolist(),
        "average_price": average_price.tolist()
    }

    return ticker, graph_data





