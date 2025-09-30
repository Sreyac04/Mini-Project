import mysql.connector
from mysql.connector import Error

def test_database_connection():
    try:
        # Database connection parameters
        connection = mysql.connector.connect(
            host='localhost',
            database='book_engine',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            print("Successfully connected to the database")
            
            # Create a cursor object
            cursor = connection.cursor()
            
            # Test query to check if new_book_table exists and has data
            cursor.execute("SELECT COUNT(*) FROM new_book_table")
            count = cursor.fetchone()[0]
            print(f"Found {count} books in new_book_table")
            
            # Test query to get a sample book
            cursor.execute("SELECT book_id, title FROM new_book_table LIMIT 1")
            sample_book = cursor.fetchone()
            if sample_book:
                print(f"Sample book: ID={sample_book[0]}, Title={sample_book[1]}")
            else:
                print("No books found in new_book_table")
            
            # Close cursor and connection
            cursor.close()
            connection.close()
            print("Database connection closed")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_database_connection()