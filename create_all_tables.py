import mysql.connector
from mysql.connector import Error

def create_tables():
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
            create_reading_progress_table_query = """
            CREATE TABLE IF NOT EXISTS reading_progress_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                page_number INT DEFAULT 1,
                paused_word VARCHAR(255),
                paused_sentence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            )
            """
            
            cursor.execute(create_reading_progress_table_query)
            print("reading_progress_table created or already exists")
            
            # Create rating_table
            create_rating_table_query = """
            CREATE TABLE IF NOT EXISTS rating_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                rating INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            )
            """
            
            cursor.execute(create_rating_table_query)
            print("rating_table created or already exists")
            
            # Create feedback_table
            create_feedback_table_query = """
            CREATE TABLE IF NOT EXISTS feedback_table (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                feedback TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            )
            """
            
            cursor.execute(create_feedback_table_query)
            print("feedback_table created or already exists")
            
            # Check the structure of all tables
            tables = ['reading_progress_table', 'rating_table', 'feedback_table']
            for table in tables:
                print(f"\n--- Checking {table} ---")
                try:
                    cursor.execute(f"DESCRIBE {table}")
                    records = cursor.fetchall()
                    print(f"{table} structure:")
                    for row in records:
                        print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
                except Error as e:
                    print(f"Error checking {table}:", e)
            
            connection.commit()
            print("\nAll tables created successfully!")
            
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
    create_tables()