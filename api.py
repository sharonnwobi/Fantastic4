from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from database.connection import connect_to_database

app = Flask("api")
api = Api(app)

class Stocks(Resource):
    def get(self):
        db = connect_to_database()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM stocks")
        stocks = cursor.fetchall()
        cursor.close()
        return jsonify(stocks)

api.add_resource(Stocks, '/api/stocks')

if __name__ == '__main__':
    app.run(debug=True)
