import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import app, mysql

def check_rating_table():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("DESCRIBE rating_table")
            columns = cur.fetchall()
            print("rating_table structure:")
            for column in columns:
                print(column)
            cur.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_rating_table()