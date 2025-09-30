import mysql.connector
from mysql.connector import Error
from app import app, mysql

def check_table_structure():
    with app.app_context():
        try:
            print("Checking new_book_table structure...")
            
            # Test connection
            cur = mysql.connection.cursor()
            
            # Describe the table
            cur.execute("DESCRIBE new_book_table")
            columns = cur.fetchall()
            
            print("Columns in new_book_table:")
            for column in columns:
                print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
                
            cur.close()
            print("Table structure check completed")
            
        except Exception as e:
            print(f"Error during table structure check: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_table_structure()

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
        
        # Check feedback_table structure
        print("--- Checking feedback_table ---")
        try:
            cursor.execute("DESCRIBE feedback_table")
            records = cursor.fetchall()
            print("feedback_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking feedback_table:", e)
        
        # Check rating_table structure
        print("\n--- Checking rating_table ---")
        try:
            cursor.execute("DESCRIBE rating_table")
            records = cursor.fetchall()
            print("rating_table structure:")
            for row in records:
                print(f"  {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
        except Error as e:
            print("Error checking rating_table:", e)
            
        # Check reading_progress_table structure
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