import mysql.connector
from mysql.connector import Error

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
        
        # Create reading_progress_table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS reading_progress_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            book_id INT NOT NULL,
            page_number INT DEFAULT 1,
            paused_word VARCHAR(255),
            paused_sentence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_table(user_id),
            FOREIGN KEY (book_id) REFERENCES new_book_table(book_id)
        )
        """
        
        cursor.execute(create_table_query)
        print("reading_progress_table created or already exists")
        
        # Check the structure of rating_table
        print("\n--- Checking rating_table ---")
        try:
            cursor.execute("DESCRIBE rating_table")
            records = cursor.fetchall()
            print("rating_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking rating_table:", e)
        
        # Check the structure of feedback_table
        print("\n--- Checking feedback_table ---")
        try:
            cursor.execute("DESCRIBE feedback_table")
            records = cursor.fetchall()
            print("feedback_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking feedback_table:", e)
            
        # Check the structure of reading_progress_table
        print("\n--- Checking reading_progress_table ---")
        try:
            cursor.execute("DESCRIBE reading_progress_table")
            records = cursor.fetchall()
            print("reading_progress_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking reading_progress_table:", e)

except Error as e:
    print("Error while connecting to MySQL:", e)
except Exception as e:
    print("General error:", e)
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL connection is closed")