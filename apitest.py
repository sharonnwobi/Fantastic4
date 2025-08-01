import yfinance as yf

stock = yf.Ticker("AMZN")
info = stock.info
print(info["shortName"], info["regularMarketPrice"])
