from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Check if books have content
        book_ids = [1, 4, 18, 29, 30]
        cur.execute("SELECT book_id, title, LENGTH(content) as content_length FROM new_book_table WHERE book_id IN (1, 4, 18, 29, 30)")
        books = cur.fetchall()
        
        print("Books with content:")
        for book in books:
            has_content = "Yes" if book[2] and book[2] > 0 else "No"
            print(f"ID {book[0]}: '{book[1]}' - Has content: {has_content} (Length: {book[2] if book[2] else 0})")
        
        cur.close()
    except Exception as e:
        print(f"Error: {e}")