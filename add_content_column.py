from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Add content column to new_book_table
        cur.execute("ALTER TABLE new_book_table ADD COLUMN content LONGTEXT")
        mysql.connection.commit()
        
        print("Content column added successfully!")
        
        # Verify the column was added
        cur.execute("DESCRIBE new_book_table")
        columns = cur.fetchall()
        print("\nAll columns in new_book_table:")
        for column in columns:
            print(f"  {column[0]} - {column[1]}")
            
        cur.close()
    except Exception as e:
        print(f"Error: {e}")