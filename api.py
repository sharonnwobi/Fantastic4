from flask import Flask, request, jsonify
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class Stocks(Resource):
    def get(self):
        db = get_db_connection() #placeholder for actual database connection
        cursor = db.cursor()
        cursor.execute("SELECT * FROM stocks")
        stocks = cursor.fetchall()
        cursor.close()
        return jsonify(stocks)

if __name__ == '__main__':
    app.run(debug=True)
