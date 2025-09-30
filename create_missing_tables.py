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
        
        # Create rating_table if it doesn't exist
        create_rating_table_query = """
        CREATE TABLE IF NOT EXISTS rating_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            book_id INT NOT NULL,
            rating INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_table(user_id),
            FOREIGN KEY (book_id) REFERENCES new_book_table(book_id)
        )
        """
        
        cursor.execute(create_rating_table_query)
        print("rating_table created or already exists")
        
        # Create feedback_table if it doesn't exist
        create_feedback_table_query = """
        CREATE TABLE IF NOT EXISTS feedback_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            book_id INT NOT NULL,
            feedback TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_table(user_id),
            FOREIGN KEY (book_id) REFERENCES new_book_table(book_id)
        )
        """
        
        cursor.execute(create_feedback_table_query)
        print("feedback_table created or already exists")
        
        # Verify all tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nAll tables in database:")
        for table in tables:
            print(f"  - {table[0]}")

except Error as e:
    print("Error while connecting to MySQL:", e)
except Exception as e:
    print("General error:", e)
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL connection is closed")