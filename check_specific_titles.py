from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Check specific book IDs
        book_ids = [1, 4, 18, 29, 30]
        cur.execute("SELECT book_id, title FROM new_book_table WHERE book_id IN (1, 4, 18, 29, 30)")
        books = cur.fetchall()
        
        print("Specific books:")
        for book in books:
            print(f"  {book[0]}: {book[1]}")
        
        cur.close()
    except Exception as e:
        print(f"Error: {e}")