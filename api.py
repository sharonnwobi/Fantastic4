from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from database.connection import connect_to_database

app = Flask("api")
api = Api(app)

class Stocks(Resource):
    def get(self):
        db = connect_to_database()
        cursor = db.cursor(dictionary=True) #using dictonary
        cursor.execute("SELECT * FROM stocks")
        stocks = cursor.fetchall()
        cursor.close()
        return jsonify(stocks)

class Portfolio(Resource):
    def get(self):
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM portfolio")
        portfolio = cursor.fetchall()
        cursor.close()
        return jsonify(portfolio)

api.add_resource(Stocks, '/api/stocks')
api.add_resource(Portfolio, '/api/portfolio')

if __name__ == '__main__':
    app.run(debug=True)
