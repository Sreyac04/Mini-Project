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
    cursor.execute("DESCRIBE new_book_table")
    columns = cursor.fetchall()
    
    print("Columns in new_book_table:")
    content_column_exists = False
    for column in columns:
        print(f"  {column[0]} - {column[1]}")
        if column[0] == 'content':
            content_column_exists = True
    
    if content_column_exists:
        print("\n✓ Content column exists in new_book_table")
    else:
        print("\n✗ Content column does NOT exist in new_book_table")
        
    # Check if there's any content in the table
    if content_column_exists:
        cursor.execute("SELECT book_id, title, LENGTH(content) as content_length FROM new_book_table WHERE content IS NOT NULL AND content != '' LIMIT 5")
        books_with_content = cursor.fetchall()
        
        if books_with_content:
            print(f"\nFound {len(books_with_content)} books with content:")
            for book in books_with_content:
                print(f"  ID: {book[0]}, Title: {book[1]}, Content Length: {book[2]} characters")
        else:
            print("\nNo books with content found")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")