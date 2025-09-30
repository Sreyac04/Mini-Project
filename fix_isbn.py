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
        
        print("Updating ISBN field to support longer ISBNs...")
        # Update ISBN field to support longer ISBNs (up to 20 characters)
        cur.execute('ALTER TABLE new_book_table MODIFY COLUMN ISBN varchar(20)')
        mysql.connection.commit()
        
        print("ISBN field updated successfully!")
        
        # Verify the change
        cur.execute('DESCRIBE new_book_table')
        structure = cur.fetchall()
        for col in structure:
            if col[0] == 'ISBN':
                print(f'New ISBN field definition: {col[0]} - {col[1]}')
        
        cur.close()
        
    except Exception as e:
        print(f'Database error: {e}')