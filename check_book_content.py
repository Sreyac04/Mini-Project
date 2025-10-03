import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='book_engine'
    )
    cursor = conn.cursor()
    
    # Check books with content
    cursor.execute("SELECT book_id, title, author, LENGTH(content) as content_length FROM new_book_table WHERE content IS NOT NULL AND content != '' ORDER BY book_id")
    books_with_content = cursor.fetchall()
    
    print("Books with content in the database:")
    print("=" * 80)
    for book in books_with_content:
        print(f"ID: {book[0]:2d} | Title: {book[1]:30s} | Author: {book[2]:20s} | Content Length: {book[3]} characters")
    
    # Show content of the first book as an example
    if books_with_content:
        first_book_id = books_with_content[0][0]
        cursor.execute("SELECT title, content FROM new_book_table WHERE book_id = %s", (first_book_id,))
        book_data = cursor.fetchone()
        
        if book_data and book_data[1]:
            print(f"\nContent preview for '{book_data[0]}':")
            print("=" * 80)
            content_preview = book_data[1][:500]
            print(content_preview)
            if len(book_data[1]) > 500:
                print("...")
                print(f"[Content truncated. Total length: {len(book_data[1])} characters]")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")