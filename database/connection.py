import mysql.connector
from config import HOST, USER, PASSWORD


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
        query = ("SELECT s.stock_id, s.symbol, SUM(t.price) AS total_price, SUM(t.quantity) AS total_quantity FROM transactions t JOIN stocks s ON  s.stock_id = t.stock_id GROUP BY s.symbol")
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
    print("Connected to database")
    query = "INSERT INTO portfolio_history (stock_id, timestamp_hist, avg_price) VALUES (%s, %s, %s)"
    for timestamp, price in zip(timestamps, prices):
        cursor.execute("SELECT COUNT(*) FROM portfolio_history WHERE stock_id = %s AND timestamp_hist = %s", (stock_id, timestamp))
        if cursor.fetchone()[0] == 0:
            cursor.execute(query, (stock_id, timestamp, price))
    db_connection.commit()
    cursor.close()
    db_connection.close()
    
    return {
        "timestamps": timestamps,
        "prices": prices
    }