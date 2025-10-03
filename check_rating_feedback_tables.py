from app import app, mysql

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Check rating table structure
        cur.execute('DESCRIBE rating_table')
        print('Rating Table Structure:')
        for row in cur.fetchall():
            print(f"  {row[0]} - {row[1]} - {row[2]} - {row[3]}")
        
        print('\nFeedback Table Structure:')
        cur.execute('DESCRIBE feedback_table')
        for row in cur.fetchall():
            print(f"  {row[0]} - {row[1]} - {row[2]} - {row[3]}")
        
        # Check if there's any data
        cur.execute('SELECT COUNT(*) FROM rating_table')
        rating_count = cur.fetchone()[0]
        print(f'\nTotal ratings: {rating_count}')
        
        cur.execute('SELECT COUNT(*) FROM feedback_table')
        feedback_count = cur.fetchone()[0]
        print(f'Total feedback entries: {feedback_count}')
        
        cur.close()
        
    except Exception as e:
        print(f"Error: {e}")