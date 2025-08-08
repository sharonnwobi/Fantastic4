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
    print(data["portfolioHistory"])
    portfolio_data = requests.get("http://localhost:5000/api/sidebar")
    portfolio_data = portfolio_data.json()
    return render_template("index.html", stocks=data["stocks"], history=data["history"], portfolioHistory=data["portfolioHistory"], portfolio_data=portfolio_data)


# FOR THE BUY STOCKS PAGE
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
    return render_template("create.html", stock_options=stock_options, portfolio_data=portfolio_data)


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
    return render_template("sell.html", stock_options=stock_options)

# @app.route("/stocks/edit/<int:stock_id>", methods=["GET", "POST"])
# def edit_stock(stock_id):
#     db = connect_to_database()
#     cursor = db.cursor(dictionary=True)
#     if request.method == "POST":
#         symbol = request.form["symbol"]
#         name = request.form["company_name"]
#         sector = request.form["sector"]
#         cursor.execute(
#             "UPDATE stocks SET symbol=%s, company_name=%s, sector=%s WHERE stock_id=%s",
#             (symbol, name, sector, stock_id)
#         )
#         db.commit()
#         cursor.close()
#         return redirect("/stocks")
#     else:
#         cursor.execute("SELECT * FROM stocks WHERE stock_id = %s", (stock_id,))
#         stock = cursor.fetchone()
#         cursor.close()
#         return render_template("edit.html", stock=stock)

# @app.route("/stocks/delete/<int:stock_id>")
# def delete_stock(stock_id):
#     db = connect_to_database()
#     cursor = db.cursor()
#     #Dont have to do it after the new db /cascade on portfolio/
#     cursor.execute("DELETE FROM portfolio WHERE stock_id = %s", (stock_id,))
#     cursor.execute("DELETE FROM stocks WHERE stock_id = %s", (stock_id,))
#     db.commit()
#     cursor.close()
#     return redirect("/stocks")

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
@app.route("/overview")
def overview():
    # db = connect_to_database()
    # cursor = db.cursor(dictionary=True)
    #
    # cursor.execute("""
    #     SELECT
    #         s.symbol AS stock_symbol,
    #         s.company_name,
    #         SUM(t.quantity) AS quantity
    #     FROM
    #         transactions t
    #     JOIN
    #         stocks s ON t.stock_id = s.stock_id
    #     GROUP BY
    #         s.symbol, s.company_name
    #     HAVING
    #         quantity > 0
    # """)
    # results = cursor.fetchall()


    results = requests.get("http://localhost:5000/api/overview")
    portfolio_data = []
    total_value = 0
    top_stock = None

    for row in results:
        price = get_stock_current_price(row["stock_symbol"])
        total = float(row["quantity"]) * price
        total_value += total

        stock_data = {
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



#
# @app.route("/stocks", methods=["GET", "POST"])
# def portfolio_summary():
#     portfolio = requests.get("http://localhost:5000/api/transactions")
#     portfolio = portfolio.json()







if __name__ == "__main__":
    app.run(debug=True, port=5001)
