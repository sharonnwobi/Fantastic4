from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from database.connection import (connect_to_database)
from helpers.yfinance_lookup import get_stock_info
from database.connection import view_portfolio
from database.connection import get_last_timestamp_for_stock
from helpers.yfinance_lookup import get_stock_history
from datetime import datetime
from database.connection import process_history

app = Flask("api")
api = Api(app)
class Stocks(Resource):
    def get(self, stock_id=None):
        if stock_id:
            data = get_stock_info(stock_id)
            return jsonify(data)
        else:
            data = view_portfolio()
            filtered_history = []
            for stock in data:
                last_timestamp = get_last_timestamp_for_stock(stock[1])
                if last_timestamp:
                    datetime_now = datetime.now()
                    period = "1d" if (datetime_now - last_timestamp).days < 1 else "5d"
                else:
                    period = "1d"
                history = get_stock_history(stock[1], period)
                filtered_history.append({
                    "symbol": stock[1],
                    "history": process_history(stock[0], history)
                })
            return jsonify({
                "stocks": data,
                "history": filtered_history
            })
        
class Transactions(Resource):
    def get(self):
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM portfolio")
        portfolio = cursor.fetchall()
        cursor.close()
        return jsonify(portfolio)


    def post(self):
        data = request.get_json()

        try:
            db = connect_to_database()
            cursor = db.cursor()
            cursor.execute( "CALL transactions_sproc (%s, %s, %s)", (data["stock_id"], data["price"], data["quantity"]))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"Error: {e}")



api.add_resource(Stocks, '/api/stocks/<stock_id>', '/api/stocks')
api.add_resource(Transactions, '/api/transactions')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
