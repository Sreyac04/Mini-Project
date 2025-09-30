from app import app, mysql

def test_flask_database():
    with app.app_context():
        try:
            print("Testing Flask MySQL connection...")
            
            # Test connection
            cur = mysql.connection.cursor()
            print("Database connection successful")
            
            # Test if new_book_table exists
            cur.execute("SHOW TABLES LIKE 'new_book_table'")
            table_exists = cur.fetchone()
            if table_exists:
                print("new_book_table exists")
                
                # Test counting records
                cur.execute("SELECT COUNT(*) FROM new_book_table")
                count = cur.fetchone()[0]
                print(f"new_book_table contains {count} records")
                
                # Test fetching a sample record
                cur.execute("SELECT book_id, title FROM new_book_table LIMIT 1")
                sample = cur.fetchone()
                if sample:
                    print(f"Sample book: ID={sample[0]}, Title={sample[1]}")
                else:
                    print("No records found in new_book_table")
            else:
                print("new_book_table does not exist")
                
            cur.close()
            print("Test completed successfully")
            
        except Exception as e:
            print(f"Error during database test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_flask_database()