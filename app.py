from flask import Flask, render_template, request, redirect
import requests
from database.connection import connect_to_database
from helpers.yfinance_lookup import get_top_stock_info

app = Flask(__name__)

@app.route("/stocks")
def show_stocks():
    response = requests.get("http://localhost:5000/api/stocks")
    stocks = response.json()
    return render_template("index.html", stocks=stocks)

@app.route("/stocks/create", methods=["GET", "POST"])
def create_stock():
    if request.method == "POST":
        symbol = request.form["symbol"]
        name = request.form["company_name"]
        sector = request.form["sector"]
        db = connect_to_database()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO stocks (symbol, company_name, sector) VALUES (%s, %s, %s)",
            (symbol, name, sector)
        )
        db.commit()
        cursor.close()
        return redirect("/stocks")
    
    stock_options = get_top_stock_info()
    return render_template("create.html", stock_options=stock_options)


@app.route("/stocks/edit/<int:stock_id>", methods=["GET", "POST"])
def edit_stock(stock_id):
    db = connect_to_database()
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        symbol = request.form["symbol"]
        name = request.form["company_name"]
        sector = request.form["sector"]
        cursor.execute(
            "UPDATE stocks SET symbol=%s, company_name=%s, sector=%s WHERE stock_id=%s",
            (symbol, name, sector, stock_id)
        )
        db.commit()
        cursor.close()
        return redirect("/stocks")
    else:
        cursor.execute("SELECT * FROM stocks WHERE stock_id = %s", (stock_id,))
        stock = cursor.fetchone()
        cursor.close()
        return render_template("edit.html", stock=stock)
@app.route("/stocks/delete/<int:stock_id>")
def delete_stock(stock_id):
    db = connect_to_database()
    cursor = db.cursor()
    #Dont have to do it after the new db /cascade on portfolio/
    cursor.execute("DELETE FROM portfolio WHERE stock_id = %s", (stock_id,))
    cursor.execute("DELETE FROM stocks WHERE stock_id = %s", (stock_id,))
    db.commit()
    cursor.close()
    return redirect("/stocks")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
