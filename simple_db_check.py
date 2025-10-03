# Simple database connection test
import mysql.connector

try:
    print("Attempting to connect to MySQL database...")
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='book_engine'
    )
    print("✓ Successfully connected to database")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM new_book_table")
    count = cursor.fetchone()[0]
    print(f"✓ Found {count} books in new_book_table")
    
    cursor.execute("SELECT book_id, title, author FROM new_book_table LIMIT 3")
    books = cursor.fetchall()
    print("Sample books:")
    for book in books:
        print(f"  ID: {book[0]}, Title: {book[1]}, Author: {book[2]}")
    
    conn.close()
    print("✓ Database connection closed")
    
except Exception as e:
    print(f"✗ Error: {e}")