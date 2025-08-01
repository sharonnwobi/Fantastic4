import mysql.connector

def connect_to_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="happy123",
        database="finance_db"
    )
    return mydb