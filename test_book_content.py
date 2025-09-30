from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Get a book with content
        cur.execute("SELECT book_id, title, author, genre, content FROM new_book_table WHERE book_id = 1")
        book = cur.fetchone()
        
        if book:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Genre: {book[3]}")
            print(f"Content length: {len(book[4]) if book[4] else 0}")
            if book[4]:
                print(f"Content preview: {book[4][:200]}...")
            else:
                print("No content available")
        else:
            print("Book not found")
        
        cur.close()
    except Exception as e:
        print(f"Error: {e}")