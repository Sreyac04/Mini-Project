from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Check for books with titles containing specific keywords
        keywords = ['Lord of the Rings', 'Harry Potter', 'Pride and Prejudice', 'To Kill a Mockingbird', 'Great Gatsby']
        
        for keyword in keywords:
            cur.execute("SELECT book_id, title FROM new_book_table WHERE title LIKE %s", (f"%{keyword}%",))
            books = cur.fetchall()
            if books:
                print(f"Books matching '{keyword}':")
                for book in books:
                    print(f"  {book[0]}: {book[1]}")
            else:
                print(f"No books found matching '{keyword}'")
            print()
        
        cur.close()
    except Exception as e:
        print(f"Error: {e}")