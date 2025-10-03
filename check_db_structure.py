import mysql.connector

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
        
        # Check if new_book_table exists and show its structure
        print("--- Checking new_book_table ---")
        try:
            cursor.execute("DESCRIBE new_book_table")
            records = cursor.fetchall()
            print("new_book_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Exception as e:
            print("Error checking new_book_table:", e)
            
        # Check if there are any books in the table
        print("\n--- Checking books in new_book_table ---")
        try:
            cursor.execute("SELECT COUNT(*) FROM new_book_table")
            count = cursor.fetchone()[0]
            print(f"Number of books in new_book_table: {count}")
            
            if count > 0:
                cursor.execute("SELECT book_id, title, author FROM new_book_table LIMIT 5")
                books = cursor.fetchall()
                print("Sample books:")
                for book in books:
                    print(f"  ID: {book[0]}, Title: {book[1]}, Author: {book[2]}")
        except Exception as e:
            print("Error checking books:", e)
            
except Exception as e:
    print("Error while connecting to MySQL:", e)
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL connection is closed")