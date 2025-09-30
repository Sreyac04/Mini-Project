import mysql.connector
from mysql.connector import Error

def test_fix():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            database='book_engine',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Test inserting into reading_progress_table
            print("Testing reading_progress_table...")
            try:
                cursor.execute("""
                    INSERT INTO reading_progress_table 
                    (user_id, book_id, page_number, paused_word, paused_sentence) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (1, 1, 5, "test", "This is a test sentence"))
                connection.commit()
                print("✓ Successfully inserted into reading_progress_table")
            except Error as e:
                print("✗ Error inserting into reading_progress_table:", e)
            
            # Test inserting into rating_table
            print("\nTesting rating_table...")
            try:
                cursor.execute("""
                    INSERT INTO rating_table 
                    (user_id, book_id, rating) 
                    VALUES (%s, %s, %s)
                """, (1, 1, 4))
                connection.commit()
                print("✓ Successfully inserted into rating_table")
            except Error as e:
                print("✗ Error inserting into rating_table:", e)
            
            # Test inserting into feedback_table
            print("\nTesting feedback_table...")
            try:
                cursor.execute("""
                    INSERT INTO feedback_table 
                    (user_id, book_id, feedback) 
                    VALUES (%s, %s, %s)
                """, (1, 1, "This is a test feedback"))
                connection.commit()
                print("✓ Successfully inserted into feedback_table")
            except Error as e:
                print("✗ Error inserting into feedback_table:", e)
            
            # Clean up test data
            try:
                cursor.execute("DELETE FROM reading_progress_table WHERE user_id = 1 AND book_id = 1")
                cursor.execute("DELETE FROM rating_table WHERE user_id = 1 AND book_id = 1")
                cursor.execute("DELETE FROM feedback_table WHERE user_id = 1 AND book_id = 1")
                connection.commit()
                print("\n✓ Test data cleaned up successfully")
            except Error as e:
                print("✗ Error cleaning up test data:", e)
            
    except Error as e:
        print("Error while connecting to MySQL:", e)
    except Exception as e:
        print("General error:", e)
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection is closed")

if __name__ == "__main__":
    test_fix()