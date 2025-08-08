from flask import Flask, render_template, request, redirect
import requests
from database.connection import connect_to_database
from datetime import datetime
from helpers.yfinance_lookup import get_stock_current_price
from api import Stocks, Transactions, Companies, SideBar

app = Flask(__name__)

@app.route("/stocks")
def show_stocks():
    response = requests.get("http://localhost:5000/api/dashboard")
    data = response.json()
    portfolio_data = requests.get("http://localhost:5000/api/sidebar")
    portfolio_data = portfolio_data.json()
    rows = portfolio_data
    total_price = sum(float(row[2]) for row in rows)
    total_quantity = sum(float(row[3]) for row in rows)
    return render_template("index.html", stocks=data["stocks"], history=data["history"], 
                           portfolioHistory=data["portfolioHistory"], portfolio_data=portfolio_data, 
                           portfolioLabels=data["portfolioLabels"],
                           total_price=total_price, total_quantity=total_quantity)


@app.route("/stocks/create", methods=["GET", "POST"])
def create_stock():
    if request.method == "POST":

        stock_id = request.form.get("stock_id")
        quantity = float(request.form["quantity"])
        price = float(request.form.get("price")) * quantity

        payload = {"stock_id": stock_id, "price": price, "quantity": quantity}

        requests.post("http://localhost:5000/api/transactions", json=payload)
        return redirect("/stocks")

    stock_options = requests.get("http://localhost:5000/api/stocks")

    portfolio_data = requests.get("http://localhost:5000/api/sidebar").json()
    stock_options = stock_options.json()
    for stock in stock_options:
        stock["current_price"] = get_stock_current_price(stock["symbol"])
        
    stock_id = request.args.get("stock_id")
    if not stock_id:
        stock_id = None
    return render_template("create.html", stock_options=stock_options, portfolio_data=portfolio_data, stock_id=stock_id)


@app.route("/stocks/sell", methods=["GET", "POST"])
def sell_stock():
    if request.method == "POST":

        stock_id = request.form.get("stock_id")
        quantity = float(request.form.get("quantity")) * -1
        price = float(request.form.get("price")) * quantity

        payload = {"stock_id": stock_id, "price": price, "quantity": quantity}

        requests.post("http://localhost:5000/api/transactions", json=payload)
        return redirect("/stocks")

    stock_options = requests.get("http://localhost:5000/api/companies")

    stock_options = stock_options.json()
    for stock in stock_options:
        stock["current_price"] = get_stock_current_price(stock["symbol"])
    stock_id = request.args.get("stock_id")
    if not stock_id:
        stock_id = None
    return render_template("sell.html", stock_options=stock_options, stock_id=stock_id)



@app.route("/single_chartoverview", methods=["GET"])
@app.route("/single_chartoverview/<symbol>", methods=["GET"])
def stock_overview(symbol=None):
    if symbol:
        response = requests.get(f"http://localhost:5000/api/stocks/{symbol}")
        if response.status_code != 200:
            print(response.text)
            return "Error fetching stock data", 500
        data = response.json()
        info = data.get("info", {})
        timestamps = data.get("timestamps", [])
        prices = data.get("prices", [])
    else:
        info = {}
        timestamps = []
        prices = []

    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT symbol FROM stocks")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    stock_list = [row["symbol"] for row in rows]
    return render_template(
        "singlechart_overview.html",
        info=info,
        timestamps=timestamps,
        prices=prices,
        stock_list=stock_list,
        selected_symbol=symbol
    )
@app.route("/overview")
def overview():
    results = requests.get("http://localhost:5000/api/overview").json()
    portfolio_data = []
    total_value = 0
    top_stock = None

    for row in results:
        price = get_stock_current_price(row["stock_symbol"])
        total = float(row["quantity"]) * price
        total_value += total

        stock_data = {
            "stock_id": row["stock_id"],
            "symbol": row["stock_symbol"],
            "company_name": row["company_name"],
            "quantity": row["quantity"],
            "current_price": round(price, 2),
            "total_value": round(total, 2)
        }

        if not top_stock or total > top_stock["total_value"]:
            top_stock = stock_data

        portfolio_data.append(stock_data)
    pf_data = requests.get("http://localhost:5000/api/sidebar")

    pf_data = pf_data.json()

    return render_template("overview.html",
                           portfolio=portfolio_data,
                           total_value=round(total_value, 2),
                           top_stock=top_stock,
                           portfolio_data=pf_data)







if __name__ == "__main__":
    app.run(debug=True, port=5001)
