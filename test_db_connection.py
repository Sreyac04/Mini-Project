from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SHOW TABLES')
        tables = cur.fetchall()
        print("Database tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if new_book_table exists
        cur.execute("SELECT COUNT(*) FROM new_book_table")
        count = cur.fetchone()[0]
        print(f"\nFound {count} books in new_book_table")
        
        # Try to get a sample book
        cur.execute("SELECT book_id, title FROM new_book_table LIMIT 1")
        sample = cur.fetchone()
        if sample:
            print(f"\nSample book: ID={sample[0]}, Title={sample[1]}")
        else:
            print("\nNo books found in new_book_table")
            
        cur.close()
    except Exception as e:
        print(f"Error: {e}")