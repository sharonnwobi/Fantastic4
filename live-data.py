from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/data/<ticker>")
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1m")
    times = data.index.strftime('%Y-%m-%d %H:%M:%S')
    average_prices = (data['Open'] + data['Close']) / 2
    return jsonify({
        "times": times.tolist(),
        "average_prices": average_prices.tolist()
    })

if __name__ == "__main__":
    app.run(debug=True, port=5002)