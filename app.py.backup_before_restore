 in post-war America.',
                'Lord of the Flies': 'William Golding\'s allegorical novel about British boys stranded on a deserted island. A dark exploration of human nature, civilization, and the thin veneer between order and chaos.',
                'Hamlet': 'Shakespeare\'s tragic masterpiece about the Prince of Denmark\'s quest for revenge against his uncle. A profound meditation on death, madness, and moral corruption that remains one of literature\'s greatest works.',
                'Macbeth': 'Shakespeare\'s dark tragedy of ambition and guilt. The story of a Scottish general whose encounter with three witches leads him down a path of murder and madness in his quest for power.',
                'The Odyssey': 'Homer\'s epic poem chronicles Odysseus\' ten-year journey home after the Trojan War. A timeless adventure filled with mythical creatures, divine intervention, and the hero\'s unwavering determination to return to his family.',
                'Don Quixote': 'Cervantes\' satirical masterpiece follows an aging gentleman who becomes a self-styled knight-errant. A humorous yet poignant exploration of idealism, reality, and the power of imagination.',
                'Moby Dick': 'Herman Melville\'s epic tale of Captain Ahab\'s obsessive quest to kill the white whale. A complex narrative that explores themes of fate, nature, and the destructive power of obsession.',
                'Les Misérables': 'Victor Hugo\'s sweeping novel of redemption set against the backdrop of 19th-century France. The story of Jean Valjean\'s transformation from convict to saint, exploring themes of justice, love, and social inequality.',
                'Anna Karenina': 'Tolstoy\'s tragic novel of a married woman\'s affair that leads to her downfall. A complex exploration of love, society, and moral responsibility in aristocratic Russian society.',
                'The Brothers Karamazov': 'Dostoevsky\'s philosophical novel about three brothers and their relationship with their despicable father. A profound exploration of faith, doubt, and the nature of good and evil.',
                'Crime and Punishment': 'Dostoevsky\'s psychological masterpiece about a young man who commits murder and struggles with guilt. A deep exploration of morality, redemption, and the human conscience.',
                'One Hundred Years of Solitude': 'García Márquez\'s magical realism masterpiece chronicles the Buendía family across seven generations. A rich tapestry of Latin American history, myth, and the cyclical nature of time.',
                'Gitanjali': 'Rabindranath Tagore\'s collection of devotional poems that won him the Nobel Prize in Literature. These spiritual verses explore themes of divine love, human devotion, and the soul\'s relationship with the infinite.'
            }
            
            # Get description for the specific book title, or generate a generic one
            description = title_descriptions.get(book_data[1], f'A compelling {book_data[3].lower()} work by {book_data[2]}. This engaging book offers readers a rich literary experience that explores profound themes and memorable characters, showcasing the author\'s unique voice and storytelling mastery.')
            
            book_info = {
                'id': book_data[0],
                'title': book_data[1],
                'author': book_data[2],
                'genre': book_data[3],
                'isbn': book_data[4],
                'rating': rating,
                'stars': stars,
                'description': description
            }
            
            return render_template('book.html', book=book_info)
        else:
            flash("Book not found.", "error")
            return redirect(url_for('recommended_books'))
            
    except Exception as e:
        flash(f"Error loading book details: {e}", "error")
        return redirect(url_for('recommended_books'))

# Read Book
@app.route("/read/<int:book_id>")
def read_book(book_id):
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT book_id, title, author, genre, ISBN FROM new_book_table WHERE book_id = %s",
            (book_id,)
        )
        book_data = cur.fetchone()
        cur.close()
        
        if book_data:
            # Generate consistent rating based on book properties (same logic as recommended_books)
            rating_seed = (book_data[0] * 7 + len(book_data[1])) % 15 + 35  # Range 35-49
            rating = round(rating_seed / 10.0, 1)  # Convert to 3.5-4.9 range
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            
            book_info = {
                'id': book_data[0],
                'title': book_data[1],
                'author': book_data[2],
                'genre': book_data[3],
                'isbn': book_data[4],
                'rating': rating,
                'stars': stars
            }
            
            return render_template('read.html', book=book_info)
        else:
            flash("Book not found.", "error")
            return redirect(url_for('recommended_books'))
            
    except Exception as e:
        flash(f"Error loading book: {e}", "error")
        return redirect(url_for('recommended_books'))

# Save Book Rating
@app.route("/save_rating", methods=["POST"])
def save_rating():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to rate books.'}), 401
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        rating = data.get('rating')
        
        # Validate input
        if not book_id or not rating:
            return jsonify({'success': False, 'message': 'Book ID and rating are required.'}), 400
        
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Rating must be an integer between 1 and 5.'}), 400
        
        # Check if book exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT book_id FROM new_book_table WHERE book_id = %s", (book_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({'success': False, 'message': 'Book not found.'}), 404
        
        # Save or update rating
        cur.execute("""
            INSERT INTO rating_table (user_id, book_id, rating) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE rating = %s
        """, (session['user_id'], book_id, rating, rating))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Rating saved successfully.'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving rating: {str(e)}'}), 500

# Save Book Feedback
@app.route("/save_feedback", methods=["POST"])
def save_feedback():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to submit feedback.'}), 401
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        feedback = data.get('feedback')
        
        # Validate input
        if not book_id or not feedback:
            return jsonify({'success': False, 'message': 'Book ID and feedback are required.'}), 400
        
        if len(feedback.strip()) < 10:
            return jsonify({'success': False, 'message': 'Feedback must be at least 10 characters long.'}), 400
        
        # Check if book exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT book_id FROM new_book_table WHERE book_id = %s", (book_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({'success': False, 'message': 'Book not found.'}), 404
        
        # Save feedback
        cur.execute("""
            INSERT INTO feedback_table (user_id, book_id, feedback) 
            VALUES (%s, %s, %s)
        """, (session['user_id'], book_id, feedback.strip()))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Feedback submitted successfully.'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving feedback: {str(e)}'}), 500

# Save reading progress
@app.route("/save_progress", methods=["POST"])
def save_progress():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to save progress.'}), 401
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        current_sentence = data.get('current_sentence', 0)
        font_size = data.get('font_size', 16)
        rating = data.get('rating', 0)
        
        # Validate input
        if book_id is None:
            return jsonify({'success': False, 'message': 'Book ID is required.'}), 400
        
        # Check if book exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT book_id FROM new_book_table WHERE book_id = %s", (book_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({'success': False, 'message': 'Book not found.'}), 404
        
        # Save or update reading progress
        cur.execute("""
            INSERT INTO reading_progress_table (user_id, book_id, current_sentence, font_size) 
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
            current_sentence = VALUES(current_sentence), 
            font_size = VALUES(font_size)
        """, (session['user_id'], book_id, current_sentence, font_size))
        
        mysql.connection.commit()
        
        # Also save rating if provided
        if rating and rating > 0:
            cur.execute("""
                INSERT INTO rating_table (user_id, book_id, rating) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE rating = %s
            """, (session['user_id'], book_id, rating, rating))
            mysql.connection.commit()
        
        cur.close()
        
        return jsonify({'success': True, 'message': 'Progress saved successfully.'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving progress: {str(e)}'}), 500

# Get reading progress
@app.route("/get_progress/<int:book_id>")
def get_progress(book_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to get progress.'}), 401
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT current_sentence, font_size 
            FROM reading_progress_table 
            WHERE user_id = %s AND book_id = %s
        """, (session['user_id'], book_id))
        progress_data = cur.fetchone()
        cur.close()
        
        if progress_data:
            return jsonify({
                'success': True,
                'progress': {
                    'current_sentence': progress_data[0],
                    'font_size': progress_data[1]
                }
            })
        else:
            return jsonify({'success': True, 'progress': None})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting progress: {str(e)}'}), 500

# Get book rating
@app.route("/get_rating/<int:book_id>")
def get_rating(book_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to get rating.'}), 401
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT rating 
            FROM rating_table 
            WHERE user_id = %s AND book_id = %s
        """, (session['user_id'], book_id))
        rating_data = cur.fetchone()
        cur.close()
        
        if rating_data:
            return jsonify({
                'success': True,
                'rating': rating_data[0]
            })
        else:
            return jsonify({'success': True, 'rating': None})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting rating: {str(e)}'}), 500

# Route to create admin user (for initial setup)
@app.route("/create_admin")
def create_admin():
    try:
        cur = mysql.connection.cursor()
        
        # Check if admin already exists
        cur.execute("SELECT user_id FROM user_table WHERE role = 'admin'")
        admin_exists = cur.fetchone()
        
        if admin_exists:
            cur.close()
            return "Admin user already exists. <a href='{}'>Go to Login</a>".format(url_for('login'))
        
        # Create default admin user
        admin_data = (
            'Admin',  # username
            'admin123',  # password (should be changed after first login)
            'admin@bookbot.com',  # email
            '9999999999',  # phone
            '1990-01-01',  # dob
            'Other',  # gender
            'admin',  # role
            'William Shakespeare',  # preferred author (can be null for admin)
            'Fiction'  # preferred genre (can be null for admin)
        )
        
        cur.execute(
            """INSERT INTO user_table 
               (username, password, email, phone_no, dob, gender, role, author, genre) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            admin_data
        )
        mysql.connection.commit()
        cur.close()
        
        return '''<div style="padding: 2rem; text-align: center; font-family: Arial, sans-serif;">
                    <h2 style="color: #10b981;">✅ Admin Account Created Successfully!</h2>
                    <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #3b82f6;">
                        <h3>Admin Login Credentials:</h3>
                        <p><strong>Email:</strong> admin@bookbot.com</p>
                        <p><strong>Password:</strong> admin123</p>
                        <p style="color: #dc2626; font-size: 0.9em;"><strong>⚠️ Important:</strong> Please change the password after first login for security!</p>
                    </div>
                    <div style="margin-top: 2rem;">
                        <a href="{}" style="background: #3b82f6; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 6px; display: inline-block;">🔑 Go to Login</a>
                    </div>
                </div>'''.format(url_for('login'))
        
    except Exception as e:
        return f"Error creating admin user: {e}. <a href='{url_for('login')}'>Go to Login</a>"

# Route to populate sample books if database is empty
@app.route("/populate_sample_books")
def populate_sample_books():
    if 'loggedin' not in session:
        return "Please log in first"
    
    try:
        cur = mysql.connection.cursor()
        
        # Check if books already exist
        cur.execute("SELECT COUNT(*) FROM new_book_table")
        book_count = cur.fetchone()[0]
        
        if book_count > 0:
            cur.close()
            return f"Database already has {book_count} books. <a href='{url_for('debug_db')}'>Back to Debug</a>"
        
        # Sample books data
        sample_books = [
            ('Pride and Prejudice', 'Jane Austen', 'Romance', '9780141439518'),
            ('Sense and Sensibility', 'Jane Austen', 'Romance', '9780141439662'),
            ('Emma', 'Jane Austen', 'Romance', '9780141439587'),
            ('To Kill a Mockingbird', 'Harper Lee', 'Fiction', '9780061120084'),
            ('1984', 'George Orwell', 'Science Fiction', '9780451524935'),
            ('Animal Farm', 'George Orwell', 'Fiction', '9780451526342'),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', '9780743273565'),
            ('Romeo and Juliet', 'William Shakespeare', 'Drama', '9780743477116'),
            ('Hamlet', 'William Shakespeare', 'Drama', '9780743477123'),
            ('Macbeth', 'William Shakespeare', 'Drama', '9780743477130'),
            ('The Catcher in the Rye', 'J.D. Salinger', 'Fiction', '9780316769174'),
            ('Lord of the Flies', 'William Golding', 'Fiction', '9780571056781'),
            ('Jane Eyre', 'Charlotte Brontë', 'Romance', '9780141441146'),
            ('Wuthering Heights', 'Emily Brontë', 'Romance', '9780141439556'),
            ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', '9780547928227'),
            ('Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 'Fantasy', '9780747532699'),
            ('Dune', 'Frank Herbert', 'Science Fiction', '9780441172719'),
            ('Foundation', 'Isaac Asimov', 'Science Fiction', '9780553293357'),
            ('The Time Machine', 'H.G. Wells', 'Science Fiction', '9780486284729'),
            ('War and Peace', 'Leo Tolstoy', 'Historical Fiction', '9780199232765')
        ]
        
        # Insert sample books
        for book in sample_books:
            cur.execute(
                "INSERT INTO new_book_table (title, author, genre, ISBN) VALUES (%s, %s, %s, %s)",
                book
            )
        
        mysql.connection.commit()
        cur.close()
        
        return f"Successfully added {len(sample_books)} sample books to the database! <a href='{url_for('recommended_books')}'>Go to Recommendations</a> | <a href='{url_for('debug_db')}'>View Debug Info</a>"
        
    except Exception as e:
        return f"Error adding sample books: {e}"

# Debug route to check database content
@app.route("/debug_db")
def debug_db():
    if 'loggedin' not in session:
        return "Please log in first"
    
    try:
        cur = mysql.connection.cursor()
        
        # Check user preferences
        cur.execute("SELECT user_id, username, author, genre FROM user_table WHERE user_id = %s", (session['user_id'],))
        user_info = cur.fetchone()
        
        # Check total books
        cur.execute("SELECT COUNT(*) FROM new_book_table")
        total_books = cur.fetchone()[0]
        
        # Get sample books
        cur.execute("SELECT book_id, title, author, genre FROM new_book_table LIMIT 5")
        sample_books = cur.fetchall()
        
        # Get all unique authors and genres
        cur.execute("SELECT DISTINCT author FROM new_book_table ORDER BY author")
        authors = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT DISTINCT genre FROM new_book_table ORDER BY genre")
        genres = [row[0] for row in cur.fetchall()]
        
        cur.close()
        
        debug_info = f"""
        <h2>Database Debug Information</h2>
        <h3>User Info:</h3>
        <p>User ID: {user_info[0] if user_info else 'None'}</p>
        <p>Username: {user_info[1] if user_info else 'None'}</p>
        <p>Preferred Author: {user_info[2] if user_info else 'None'}</p>
        <p>Preferred Genre: {user_info[3] if user_info else 'None'}</p>
        
        <h3>Book Database:</h3>
        <p>Total Books: {total_books}</p>
        
        <h4>Sample Books:</h4>
        <ul>
        {"".join([f"<li>{book[1]} by {book[2]} ({book[3]})</li>" for book in sample_books])}
        </ul>
        
        <h4>Available Authors ({len(authors)}):</h4>
        <p>{', '.join(authors[:10])}{'...' if len(authors) > 10 else ''}</p>
        
        <h4>Available Genres ({len(genres)}):</h4>
        <p>{', '.join(genres)}</p>
        
        <p><a href="{url_for('recommended_books')}">Back to Recommendations</a></p>
        <p><a href="{url_for('populate_sample_books')}">Add Sample Books (if database is empty)</a></p>
        """
        
        return debug_info
        
    except Exception as e:
        return f"Error accessing database: {e}"

# Route to setup database tables if they don't exist
@app.route("/setup_database")
def setup_database():
    try:
        cur = mysql.connection.cursor()
        
        # Create user_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_table (
                user_id INT(11) NOT NULL AUTO_INCREMENT,
                username VARCHAR(45) NOT NULL,
                password VARCHAR(45) NOT NULL,
                email VARCHAR(45) NOT NULL,
                phone_no VARCHAR(20) NOT NULL,
                role VARCHAR(45) NOT NULL DEFAULT 'user',
                dob DATE NOT NULL,
                gender VARCHAR(10) NOT NULL,
                author VARCHAR(255) DEFAULT NULL,
                genre VARCHAR(100) DEFAULT NULL,
                PRIMARY KEY (user_id),
                UNIQUE KEY email (email)
            ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1
        """)
        
        # Create new_book_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS new_book_table (
                book_id INT(11) NOT NULL AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                ISBN VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (book_id),
                UNIQUE KEY unique_isbn (ISBN),
                INDEX idx_title (title),
                INDEX idx_author (author),
                INDEX idx_genre (genre)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create favorite_book_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS favorite_book_table (
                fav_id INT(11) NOT NULL AUTO_INCREMENT,
                user_id INT(11) NOT NULL,
                book_id INT(11) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (fav_id),
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_book (user_id, book_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create rating_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rating_table (
                rating_id INT(11) NOT NULL AUTO_INCREMENT,
                user_id INT(11) NOT NULL,
                book_id INT(11) NOT NULL,
                rating INT(1) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (rating_id),
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_book_rating (user_id, book_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create feedback_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback_table (
                feedback_id INT(11) NOT NULL AUTO_INCREMENT,
                user_id INT(11) NOT NULL,
                book_id INT(11) NOT NULL,
                feedback TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (feedback_id),
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create reading_progress_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reading_progress_table (
                progress_id INT(11) NOT NULL AUTO_INCREMENT,
                user_id INT(11) NOT NULL,
                book_id INT(11) NOT NULL,
                current_sentence INT(11) DEFAULT 0,
                font_size INT(11) DEFAULT 16,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (progress_id),
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_book_progress (user_id, book_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        mysql.connection.commit()
        cur.close()
        
        return f"Database tables created successfully! <a href='{url_for('debug_login')}'>→ Check Debug Info</a> | <a href='{url_for('create_admin')}'>→ Create Admin</a>"
        
    except Exception as e:
        return f"Error setting up database: {e}"

# Simple database test route
@app.route("/test_db")
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        
        if result:
            return "Database connection successful! <a href='/setup_database'>Setup Tables</a> | <a href='/create_admin'>Create Admin</a> | <a href='/login'>Login</a>"
        else:
            return "Database connection failed"
    except Exception as e:
        return f"Database error: {e}. Please check if MySQL server is running and database 'book_engine' exists."

@app.route("/recreate_rating_table")
def recreate_rating_table():
    try:
        cur = mysql.connection.cursor()
        
        # Drop the existing table
        cur.execute("DROP TABLE IF EXISTS rating_table")
        
        # Recreate the table with correct foreign key references
        cur.execute("""
            CREATE TABLE rating_table (
                rating_id INT(11) NOT NULL AUTO_INCREMENT,
                user_id INT(11) NOT NULL,
                book_id INT(11) NOT NULL,
                rating INT(1) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (rating_id),
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_book_rating (user_id, book_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        mysql.connection.commit()
        cur.close()
        
        return "rating_table recreated successfully with correct foreign key references!"
        
    except Exception as e:
        return f"Error recreating rating_table: {e}"

@app.route("/recreate_feedback_table")
def recreate_feedback_table():
    try:
        cur = mysql.connection.cursor()
        
        # Drop the existing table
        cur.execute("DROP TABLE IF EXISTS feedback_table")
        
        # Recreate the table with correct foreign key references
        cur.execute("""
            CREATE TABLE feedback_table (
                feedback_id INT(11) NOT NULL AUTO_INCREMENT,
                user_id INT(11) NOT NULL,
                book_id INT(11) NOT NULL,
                feedback TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (feedback_id),
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        mysql.connection.commit()
        cur.close()
        
        return "feedback_table recreated successfully with correct foreign key references!"
        
    except Exception as e:
        return f"Error recreating feedback_table: {e}"

@app.route("/recreate_reading_progress_table")
def recreate_reading_progress_table():
    try:
        cur = mysql.connection.cursor()
        
        # Drop the existing table
        cur.execute("DROP TABLE IF EXISTS reading_progress_table")
        
        # Recreate the table with correct foreign key references
        cur.execute("""
            CREATE TABLE reading_progress_table (
                progress_id INT(11) NOT NULL AUTO_INCREMENT,
                user_id INT(11) NOT NULL,
                book_id INT(11) NOT NULL,
                current_sentence INT(11) DEFAULT 0,
                font_size INT(11) DEFAULT 16,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (progress_id),
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_book_progress (user_id, book_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        mysql.connection.commit()
        cur.close()
        
        return "reading_progress_table recreated successfully with correct foreign key references!"
        
    except Exception as e:
        return f"Error recreating reading_progress_table: {e}"



@app.route("/list_tables")
def list_tables():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        cur.close()
        
        table_list = "<br>".join([table[0] for table in tables])
        return f"Database tables:<br>{table_list}"
        
    except Exception as e:
        return f"Error listing tables: {e}"


@app.route("/test_reading_progress_table")
def test_reading_progress_table():
    try:
        cur = mysql.connection.cursor()
        # Try to query the reading_progress_table
        cur.execute("SELECT * FROM reading_progress_table LIMIT 1")
        result = cur.fetchone()
        cur.close()
        
        if result is not None:
            return "Reading progress table exists and is accessible!"
        else:
            return "Reading progress table exists but is empty."
    except Exception as e:
        return f"Error accessing reading progress table: {e}"


@app.route("/fix_foreign_keys")
def fix_foreign_keys():
    try:
        cur = mysql.connection.cursor()
        results = []
        
        # Tables to fix
        tables = ['reading_progress_table', 'rating_table', 'feedback_table']
        
        for table_name in tables:
            results.append(f"--- Processing {table_name} ---")
            
            # Get current foreign key constraints
            cur.execute("""
                SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = 'book_engine' 
                AND TABLE_NAME = %s 
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (table_name,))
            constraints = cur.fetchall()
            
            # Drop any foreign key constraints that reference book_table
            for constraint_name, referenced_table in constraints:
                if referenced_table == 'book_table':
                    try:
                        cur.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}")
                        results.append(f"Dropped foreign key constraint {constraint_name} from {table_name}")
                    except Exception as e:
                        results.append(f"Warning: Could not drop constraint {constraint_name} from {table_name}: {e}")
            
            # Check if the correct foreign key constraint exists
            correct_fk_exists = False
            for constraint_name, referenced_table in constraints:
                if referenced_table == 'new_book_table':
                    correct_fk_exists = True
                    results.append(f"Correct foreign key constraint already exists in {table_name}: {constraint_name}")
                    break
            
            # If the correct foreign key doesn't exist, add it
            if not correct_fk_exists:
                constraint_name = f"fk_{table_name}_new_book"
                try:
                    cur.execute(f"""
                        ALTER TABLE {table_name} 
                        ADD CONSTRAINT {constraint_name} 
                        FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
                    """)
                    mysql.connection.commit()
                    results.append(f"Added correct foreign key constraint to {table_name}: {constraint_name}")
                except Exception as e:
                    results.append(f"Error adding constraint to {table_name}: {e}")
            else:
                results.append(f"Foreign key constraint for {table_name} is already correct")
        
        cur.close()
        return "<br>".join(results)
                
    except Exception as e:
        return f"Error fixing foreign key constraints: {e}"


@app.route("/check_rating_table")
def check_rating_table():
    try:
        cur = mysql.connection.cursor()
        cur.execute("DESCRIBE rating_table")
        columns = cur.fetchall()
        cur.close()
        
        result = "<h2>rating_table structure:</h2><ul>"
        for column in columns:
            result += f"<li>{column}</li>"
        result += "</ul>"
        
        return result
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)