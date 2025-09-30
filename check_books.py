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
        cur.execute('SELECT book_id, title FROM new_book_table')
        books = cur.fetchall()
        print('Books in database:')
        for book in books:
            print(f'  {book[0]}: {book[1]}')
        cur.close()
    except Exception as e:
        print(f"Error: {e}")
