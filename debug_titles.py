from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Get all book titles to see exact format
        cur.execute("SELECT book_id, title FROM new_book_table WHERE book_id IN (1, 4, 18, 29, 30)")
        books = cur.fetchall()
        
        print("Exact book titles:")
        for book in books:
            print(f"ID {book[0]}: '{book[1]}' (length: {len(book[1])})")
            # Show any special characters
            for i, char in enumerate(book[1]):
                if ord(char) > 127:
                    print(f"  Special character at position {i}: {repr(char)}")
        
        cur.close()
    except Exception as e:
        print(f"Error: {e}")