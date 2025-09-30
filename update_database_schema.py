import mysql.connector
from mysql.connector import Error

def update_database_schema():
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
            
            # First, drop foreign key constraints that reference book_table
            print("Dropping foreign key constraints...")
            
            # Drop foreign key constraints in rating_table
            try:
                cursor.execute("ALTER TABLE rating_table DROP FOREIGN KEY fk_rating_book")
                print("Dropped foreign key constraint fk_rating_book")
            except Error as e:
                print(f"Note: fk_rating_book constraint may not exist: {e}")
            
            # Drop foreign key constraints in feedback_table
            try:
                cursor.execute("ALTER TABLE feedback_table DROP FOREIGN KEY fk_feedback_book")
                print("Dropped foreign key constraint fk_feedback_book")
            except Error as e:
                print(f"Note: fk_feedback_book constraint may not exist: {e}")
            
            # Now update the foreign key references to point to new_book_table
            print("Updating foreign key references...")
            
            # Add new foreign key constraints referencing new_book_table
            try:
                cursor.execute("""
                    ALTER TABLE rating_table 
                    ADD CONSTRAINT fk_rating_new_book 
                    FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) 
                    ON DELETE CASCADE
                """)
                print("Added foreign key constraint fk_rating_new_book")
            except Error as e:
                print(f"Note: Could not add fk_rating_new_book constraint: {e}")
            
            try:
                cursor.execute("""
                    ALTER TABLE feedback_table 
                    ADD CONSTRAINT fk_feedback_new_book 
                    FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) 
                    ON DELETE CASCADE
                """)
                print("Added foreign key constraint fk_feedback_new_book")
            except Error as e:
                print(f"Note: Could not add fk_feedback_new_book constraint: {e}")
            
            # Finally, drop the old book_table
            print("Dropping old book_table...")
            try:
                cursor.execute("DROP TABLE IF EXISTS book_table")
                print("Dropped book_table successfully")
            except Error as e:
                print(f"Note: Could not drop book_table: {e}")
            
            connection.commit()
            print("Database schema updated successfully!")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    update_database_schema()