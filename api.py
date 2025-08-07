from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from database.connection import (connect_to_database)
from helpers.yfinance_lookup import get_stock_info
from database.connection import view_portfolio
from database.connection import get_last_timestamp_for_stock
from helpers.yfinance_lookup import get_stock_history
from datetime import datetime
from database.connection import process_history
from database.connection import view_portfolio
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
        cursor.execute("""
                       SELECT transactions.*, stocks.symbol, stocks.company_name
                       FROM transactions JOIN stocks ON transactions.stock_id = stocks.stock_id;
                       """)
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


    # def get(self):
    #     #data = request.get_json()
    #     try:
    #         db = connect_to_database()
    #         cursor = db.cursor()
    #         query = ("SELECT s.stock_id, s.symbol, SUM(t.price) AS total_price, SUM(t.quantity) AS total_quantity FROM transactions t JOIN stocks s ON  s.stock_id = t.stock_id GROUP BY s.symbol")
    #         cursor.execute(query)
    #         results = cursor.fetchall()
    #         cursor.close()
    #         #return results
    #         return jsonify(results)
    #     except Exception as e:
    #         print(f"Error: {e}")


        # finally:
        #     db.rollback()



class Companies(Resource):
    def get(self):
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT stocks.stock_id, stocks.symbol, stocks.company_name, stocks.sector, SUM(quantity) as total FROM transactions JOIN stocks ON transactions.stock_id = stocks.stock_id GROUP BY symbol HAVING total > 0;
        """)
        stocks = cursor.fetchall()
        cursor.close()
        return jsonify(stocks)




class SideBar(Resource):
    def get(self):
        return jsonify(view_portfolio())

api.add_resource(Stocks, '/api/stocks/<stock_id>', '/api/stocks')
api.add_resource(Transactions, '/api/transactions')
api.add_resource(Companies, '/api/companies')
api.add_resource(SideBar, '/api/sidebar')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
