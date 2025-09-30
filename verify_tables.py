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
        cursor = connection.cursor()
        
        # List all tables in the database
        print("--- Listing all tables ---")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in book_engine database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if our new tables exist
        new_tables = ['reading_progress_table', 'rating_table', 'feedback_table']
        for table_name in new_tables:
            print(f"\n--- Checking {table_name} ---")
            try:
                cursor.execute(f"DESCRIBE {table_name}")
                records = cursor.fetchall()
                print(f"{table_name} structure:")
                for row in records:
                    print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
            except Error as e:
                print(f"Error checking {table_name}:", e)

except Error as e:
    print("Error while connecting to MySQL:", e)
except Exception as e:
    print("General error:", e)
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL connection is closed")