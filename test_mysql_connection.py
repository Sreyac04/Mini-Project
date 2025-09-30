import mysql.connector
from mysql.connector import Error
import sys

def test_mysql_connection():
    try:
        print("Attempting to connect to MySQL database...")
        connection = mysql.connector.connect(
            host='localhost',
            database='book_engine',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"You're connected to database: {record}")
            
            # Test the new_book_table
            cursor.execute("SHOW TABLES LIKE 'new_book_table';")
            table_exists = cursor.fetchone()
            if table_exists:
                print("new_book_table exists")
                cursor.execute("SELECT COUNT(*) FROM new_book_table;")
                count = cursor.fetchone()[0]
                print(f"new_book_table contains {count} records")
            else:
                print("new_book_table does not exist")
            
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        print(f"Error code: {e.errno}")
        print(f"SQL state: {e.sqlstate}")
        if e.errno == 1045:
            print("Access denied - check username and password")
        elif e.errno == 2003:
            print("Can't connect to MySQL server - check if MySQL is running")
        elif e.errno == 1049:
            print("Unknown database - check database name")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_mysql_connection()