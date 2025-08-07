import mysql.connector
from config import HOST, USER, PASSWORD
from datetime import datetime


def connect_to_database():
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database="finance_db"
    )
    return mydb


def get_stocks():
    try:
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        print("Connected to database")

        query = "SELECT * FROM stocks"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result


    except Exception as e:
        print(e)

    except Exception:
        raise ConnectionError("Failed to connect to database")

    finally:
        db_connection.close()


def view_portfolio():
    try:
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        print("Connected to database")
        query = ("SELECT s.stock_id, s.symbol, SUM(t.price) AS total_price, SUM(t.quantity) AS total_quantity FROM transactions t JOIN stocks s ON  s.stock_id = t.stock_id GROUP BY s.symbol HAVING total_quantity > 0")
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    except Exception as e:
        print(e)

    except Exception:
        raise ConnectionError("Failed to connect to database")

    finally:
        db_connection.close()
        
def get_last_timestamp_for_stock(symbol):
    try:
        db_connection = connect_to_database()
        cursor = db_connection.cursor()
        print("Connected to database")
        query = "SELECT MAX(timestamp_hist) FROM portfolio_history WHERE stock_id = (SELECT stock_id FROM stocks WHERE symbol = %s)"
        cursor.execute(query, (symbol,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    except Exception as e:
        print(e)

    except Exception:
        raise ConnectionError("Failed to connect to database")

    finally:
        db_connection.close()

def process_history(stock_id, history):
    timestamps = history['timestamps']
    prices = history['prices']
    db_connection = connect_to_database()
    cursor = db_connection.cursor()
    query = "INSERT INTO portfolio_history (stock_id, timestamp_hist, avg_price) VALUES (%s, %s, %s)"
    for timestamp, price in zip(timestamps, prices):
        cursor.execute("SELECT COUNT(*) FROM portfolio_history WHERE stock_id = %s AND timestamp_hist = %s", (stock_id, timestamp))
        if cursor.fetchone()[0] == 0:
            cursor.execute(query, (stock_id, timestamp, price))
    db_connection.commit()
    cursor.close()
    
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT timestamp_hist, avg_price FROM portfolio_history WHERE stock_id = %s ORDER BY timestamp_hist", (stock_id,))
    history_data = cursor.fetchall()
    timestamps = [row['timestamp_hist'].strftime('%Y-%m-%d %H:%M') for row in history_data]
    prices = [row['avg_price'] for row in history_data]
    cursor.close()
    db_connection.close()
    
    return {
        "timestamps": timestamps,
        "prices": prices
    }
    
def get_all_transactions():
    try:
        db_connection = connect_to_database()
        cursor = db_connection.cursor(dictionary=True)
        print("Connected to database")
        cursor.execute("SELECT stock_id, price, quantity, transaction_date FROM transactions")

        result = []
        for row in cursor.fetchall():
            stock_id = row['stock_id']
            price = float(row['price'])
            quantity = float(row['quantity'])
            timestamp = row['transaction_date']

            result.append({
                "stock_id": stock_id,
                "price": price,
                "quantity": quantity,
                "timestamp": timestamp
            })
        cursor.close()
        return result
    except Exception as e:
        print(e)

def calculate_portfolio_value_over_time(filtered_history, transactions):
    if not filtered_history:
        return []

    timestamps = filtered_history[0]['history']['timestamps']
    portfolio_value = [0.0] * len(timestamps)

    for stock in filtered_history:
        stock_id = stock['stock_id']
        prices = stock['history']['prices']
        stock_timestamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M') for ts in stock['history']['timestamps']]

        print(stock_timestamps, prices)
        stock_transactions = sorted(
            [t for t in transactions if t['stock_id'] == stock_id],
            key=lambda t: t['timestamp']
        )

        quantity_over_time = []
        current_quantity = 0
        tx_index = 0

        for ts in stock_timestamps:
            while tx_index < len(stock_transactions) and stock_transactions[tx_index]['timestamp'] <= ts:
                current_quantity += stock_transactions[tx_index]['quantity']
                tx_index += 1

            quantity_over_time.append(current_quantity)

        for i in range(len(portfolio_value)):
            portfolio_value[i] += prices[i] * quantity_over_time[i]

    return [round(v, 2) for v in portfolio_value]