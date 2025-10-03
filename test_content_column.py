import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='book_engine'
    )
    cursor = conn.cursor()
    
    # Check if content column exists in new_book_table
    cursor.execute("SHOW COLUMNS FROM new_book_table LIKE 'content'")
    result = cursor.fetchone()
    
    if result:
        print("✓ Content column exists in new_book_table")
        print(f"Column details: {result}")
    else:
        print("✗ Content column does NOT exist in new_book_table")
        
    # Check table structure
    cursor.execute("DESCRIBE new_book_table")
    columns = cursor.fetchall()
    
    print("\nAll columns in new_book_table:")
    for column in columns:
        print(f"  {column[0]} - {column[1]}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")