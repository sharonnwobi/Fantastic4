from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/stocks")
def show_stocks():
    response = requests.get("http://localhost:5000/api/stocks")
    stocks = response.json()
    return render_template("index.html", stocks=stocks)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
