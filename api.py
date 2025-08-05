from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from database.connection import connect_to_database
from helpers.yfinance_lookup import get_stock_info

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
    

api.add_resource(Stocks, '/api/stocks/<stock_id>', '/api/stocks')

if __name__ == '__main__':
    app.run(debug=True)
