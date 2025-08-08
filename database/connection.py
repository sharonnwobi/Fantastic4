import mysql.connector
from config import HOST, USER, PASSWORD
from datetime import datetime, timedelta, timezone
import pytz

local_tz = pytz.timezone("Europe/Budapest")

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
        
def get_symbols_for_window(start_time):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = """
    SELECT s.stock_id, s.symbol
    FROM transactions t
    JOIN stocks s ON s.stock_id = t.stock_id
    GROUP BY s.stock_id, s.symbol
    HAVING SUM(t.quantity) > 0

    UNION

    SELECT DISTINCT s.stock_id, s.symbol
    FROM transactions t
    JOIN stocks s ON s.stock_id = t.stock_id
    WHERE t.transaction_date >= %s
    """
    cursor.execute(query, (start_time,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def parse_history_to_dt_map(history_timestamps, history_prices):
    dt_map = {}
    for ts_str, price in zip(history_timestamps, history_prices):
        dt_utc = datetime.strptime(ts_str, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc)
        dt_map[dt_utc] = float(price)
    return dt_map


def calculate_portfolio_value_over_time(filtered_history, transactions, grid_dt, tz=timezone.utc):
    if not filtered_history:
        return []

    portfolio_value = [0.0] * len(grid_dt)

    for stock in filtered_history:
        stock_id = stock['stock_id']
        prices = stock['history']['prices']
        ts_strs = stock['history']['timestamps']

        price_map = parse_history_to_dt_map(ts_strs, prices)

        stock_transactions = sorted(
            [t for t in transactions if t['stock_id'] == stock_id],
            key=lambda t: t['timestamp']
        )

        stock_transactions = [
            dict(
                t,
                timestamp=(
                    t['timestamp'].astimezone(tz)
                    if t['timestamp'].tzinfo
                    else local_tz.localize(t['timestamp']).astimezone(tz)
                )
            )
            for t in stock_transactions
        ]


        quantity_over_time = []
        current_quantity = 0.0
        tx_index = 0
        n_tx = len(stock_transactions)

        last_price = None

        for i, ts in enumerate(grid_dt):
            while tx_index < n_tx and stock_transactions[tx_index]['timestamp'] <= ts:
                current_quantity += float(stock_transactions[tx_index]['quantity'])
                tx_index += 1

            quantity_over_time.append(current_quantity)

            if ts in price_map:
                last_price = price_map[ts]
            price_here = last_price if last_price is not None else 0.0

            portfolio_value[i] += price_here * current_quantity

    return [round(v, 2) for v in portfolio_value]

def generate_time_grid(minutes_step=5, tz=timezone.utc):
    now = datetime.now(tz)
    end_time = now.replace(second=0, microsecond=0)
    start_time = end_time - timedelta(days=1)

    grid = []
    t = start_time
    step = timedelta(minutes=minutes_step)
    while t <= end_time:
        grid.append(t)
        t += step
    return grid