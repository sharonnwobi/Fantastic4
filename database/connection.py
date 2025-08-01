import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="finance_db"
)

mycursor = mydb.cursor(dictionary=True) # Use column names
mycursor.execute("SELECT * FROM stocks")
result = mycursor.fetchall()

print("General query:")
for row in result:
    # print(row)
    print(f"{row["symbol"]}")

print(f"Database object {mydb}")