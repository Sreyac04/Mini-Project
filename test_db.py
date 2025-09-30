import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root'
    )
    
    if connection.is_connected():
        print("Successfully connected to MySQL database")
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("Databases:")
        for db in databases:
            print(f"  - {db[0]}")
            
        # Check if book_engine exists
        cursor.execute("USE book_engine")
        print("Using book_engine database")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables:")
        for table in tables:
            print(f"  - {table[0]}")

except Error as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"General error: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("MySQL connection closed")