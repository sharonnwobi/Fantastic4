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
from database.connection import get_all_transactions
from database.connection import calculate_portfolio_value_over_time
from database.connection import generate_time_grid
from database.connection import get_symbols_for_window

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

class Dashboard(Resource):
    def get(self):
        data = view_portfolio()
        transactions = get_all_transactions()

        grid_dt = generate_time_grid(minutes_step=5)
        grid_labels = [dt.strftime('%Y-%m-%d %H:%M') for dt in grid_dt]
        start_time = grid_dt[0]

        chart_symbols = get_symbols_for_window(start_time)

        filtered_history = []
        for stock_id, symbol in chart_symbols:
            last_timestamp = get_last_timestamp_for_stock(symbol)
            datetime_now = datetime.now()
            period = "1d" if last_timestamp and (datetime_now - last_timestamp).days < 1 else "5d"

            history = get_stock_history(symbol, period)
            processed = process_history(stock_id, history)

            filtered_history.append({
                "symbol": symbol,
                "stock_id": stock_id,
                "history": processed
            })

        portfolio_over_time = calculate_portfolio_value_over_time(
            filtered_history, transactions, grid_dt
        )

        return jsonify({
            "stocks": data,
            "history": filtered_history,
            "portfolioHistory": portfolio_over_time,
            "portfolioLabels": grid_labels
        })

class Sidebar(Resource):
    def get(self):
        return jsonify(view_portfolio())
    
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
        print(data["price"], )
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



class Overview(Resource):
    def get(self):
        db = connect_to_database()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
                SELECT 
                    s.symbol AS stock_symbol,
                    s.company_name,
                    SUM(t.quantity) AS quantity
                FROM 
                    transactions t
                JOIN 
                    stocks s ON t.stock_id = s.stock_id
                GROUP BY 
                    s.symbol, s.company_name
                HAVING 
                    quantity > 0
            """)
        results = cursor.fetchall()
        cursor.close()
        return jsonify(results)



class SideBar(Resource):
    def get(self):
        return jsonify(view_portfolio())

api.add_resource(Stocks, '/api/stocks/<stock_id>', '/api/stocks')
api.add_resource(Transactions, '/api/transactions')
api.add_resource(Companies, '/api/companies')
api.add_resource(Dashboard, '/api/dashboard')
api.add_resource(Sidebar, '/api/sidebar')
api.add_resource(Overview, '/api/overview')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
