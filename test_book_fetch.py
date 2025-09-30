from app import app, mysql

def test_book_fetch():
    with app.app_context():
        try:
            print("Testing book fetch from database...")
            
            # Test connection
            cur = mysql.connection.cursor()
            print("Database connection successful")
            
            # Try to fetch book with ID 1
            print("Fetching book with ID 1...")
            cur.execute("SELECT book_id, title, author, genre, ISBN, content FROM new_book_table WHERE book_id = %s", (1,))
            book_data = cur.fetchone()
            
            if book_data:
                print(f"SUCCESS: Book found")
                print(f"  ID: {book_data[0]}")
                print(f"  Title: {book_data[1]}")
                print(f"  Author: {book_data[2]}")
                print(f"  Genre: {book_data[3]}")
                print(f"  ISBN: {book_data[4]}")
                print(f"  Content length: {len(book_data[5]) if book_data[5] else 0} characters")
            else:
                print("ERROR: Book with ID 1 not found in database")
                
            cur.close()
            print("Test completed")
            
        except Exception as e:
            print(f"Error during book fetch test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_book_fetch()