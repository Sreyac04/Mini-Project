import mysql.connector
from mysql.connector import Error

try:
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        database='book_engine',
        user='root',
        password='root'
    )
    
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        
        # List all tables in the database
        print("\n--- Listing all tables ---")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in book_engine database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if rating_table exists and show its structure
        print("\n--- Checking rating_table ---")
        try:
            cursor.execute("DESCRIBE rating_table")
            records = cursor.fetchall()
            print("rating_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking rating_table:", e)
        
        # Check if feedback_table exists and show its structure
        print("\n--- Checking feedback_table ---")
        try:
            cursor.execute("DESCRIBE feedback_table")
            records = cursor.fetchall()
            print("feedback_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking feedback_table:", e)
            
        # Check if book_table exists and show its structure
        print("\n--- Checking book_table ---")
        try:
            cursor.execute("DESCRIBE book_table")
            records = cursor.fetchall()
            print("book_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking book_table:", e)

except Error as e:
    print("Error while connecting to MySQL:", e)
except Exception as e:
    print("General error:", e)
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL connection is closed")