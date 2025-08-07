from flask import Flask, render_template, request, redirect
import requests
from database.connection import connect_to_database
from datetime import datetime
from helpers.yfinance_lookup import get_stock_current_price

app = Flask(__name__)

@app.route("/stocks")
def show_stocks():
    response = requests.get("http://localhost:5000/api/stocks")
    stocks = response.json()
    return render_template("index.html", stocks=stocks)

# FOR THE BUY STOCKS PAGE
@app.route("/stocks/create", methods=["GET", "POST"])
def create_stock():
    if request.method == "POST":

        stock_id = request.form.get("stock_id")
        price = request.form.get("price")
        quantity = request.form["quantity"]

        payload = {"stock_id": stock_id, "price": price, "quantity": quantity}

        requests.post("http://localhost:5000/api/transactions", json=payload)
        return redirect("/stocks")

    stock_options = requests.get("http://localhost:5000/api/stocks")

    stock_options = stock_options.json()
    for stock in stock_options:
        stock["current_price"] = get_stock_current_price(stock["symbol"])
    return render_template("create.html", stock_options=stock_options)



#TO SEE PARTICULAR STOCKS ON OVERVIEW PAGE FOR STATED STOCK
@app.route("/stocks/<symbol>")
def stock_overview(symbol):
    response = requests.get("http://localhost:5000/api/stocks/" + symbol)
    if response.status_code != 200:
        print(response.text)
        return "Error fetching stock data", 500
    data = response.json()
    info = data.get("info", {})
    timestamps = data.get("timestamps", [])
    prices = data.get("prices", [])

    return render_template("overview.html", info=info, timestamps=timestamps, prices=prices)







if __name__ == "__main__":
    app.run(debug=True, port=5001)
