from flask_mysqldb import MySQL
from flask import Flask

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_engine'

mysql = MySQL(app)

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Show the most recent 10 books
        cur.execute('SELECT book_id, title, author, genre, ISBN FROM book_table ORDER BY book_id DESC LIMIT 10')
        recent_books = cur.fetchall()
        print('Most recent 10 books:')
        for book in recent_books:
            print(f'  ID: {book[0]}, Title: "{book[1]}", Author: "{book[2]}", Genre: "{book[3]}", ISBN: "{book[4]}"')
        
        # Check ISBN field length constraint
        cur.execute('DESCRIBE book_table')
        structure = cur.fetchall()
        for col in structure:
            if col[0] == 'ISBN':
                print(f'ISBN field definition: {col[0]} - {col[1]}')
        
        cur.close()
        
    except Exception as e:
        print(f'Database error: {e}')