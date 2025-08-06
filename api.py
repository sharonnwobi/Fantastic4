from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from database.connection import (connect_to_database)
from helpers.yfinance_lookup import get_stock_info
from datetime import  datetime

app = Flask("api")
api = Api(app)
class Stocks(Resource):
    def get(self, stock_id=None):
        if stock_id:
            data = get_stock_info(stock_id)
            return jsonify(data)
        else:
            db = connect_to_database()
            cursor = db.cursor(dictionary=True) #using dictonary
            cursor.execute("SELECT * FROM stocks")
            stocks = cursor.fetchall()
            cursor.close()
            return jsonify(stocks)
        
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

        db = connect_to_database()
        cursor = db.cursor()
        cursor.execute( "CALL transactions_sproc (%s, %s, %s)", (data["stock_id"], data["price"], data["quantity"]))
        db.commit()
        cursor.close()
        return jsonify({"status": "success"}), 201



api.add_resource(Stocks, '/api/stocks/<stock_id>', '/api/stocks')
api.add_resource(Transactions, '/api/transactions')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
