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


def view_porfolio():
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