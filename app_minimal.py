from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import re
import csv
import os

app = Flask(__name__, template_folder="app/templates")
app.secret_key = "your_secret_key_here_please_change_this"

# MySQL configuration with safe initialization
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_engine'
app.config['MYSQL_CONNECT_TIMEOUT'] = 3
app.config['MYSQL_AUTOCOMMIT'] = True

# Initialize MySQL safely
mysql = None
try:
    from flask_mysqldb import MySQL
    mysql = MySQL(app)
    print("✅ MySQL extension loaded successfully")
except ImportError:
    print("❌ flask_mysqldb not installed")
except Exception as e:
    print(f"⚠️ MySQL initialization issue: {e}")

# Database connection test function
def test_database_connection():
    """Test if database connection is working"""
    if mysql is None:
        return False, "MySQL not initialized"
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)

# Simple test routes without database dependency
@app.route("/")
def landing():
    """Landing page without database dependency"""
    print("Landing page accessed - minimal version")
    return render_template("landing.html")

@app.route("/test")
def test():
    """Simple test page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Book Bot - Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1e293b; color: white; }
            .container { max-width: 600px; margin: 0 auto; text-align: center; }
            .btn { display: inline-block; padding: 10px 20px; margin: 5px; background: #7c3aed; color: white; text-decoration: none; border-radius: 5px; }
            .status { padding: 20px; background: #0f172a; border-radius: 10px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📦 Book Bot Test Page</h1>
            <div class="status">
                <h2>✅ Flask Server is Working!</h2>
                <p>If you can see this page, the Flask application is running correctly.</p>
                <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            </div>
            <div>
                <a href="/" class="btn">🏠 Go to Home Page</a>
                <a href="/login" class="btn">🔑 Login</a>
            </div>
            <p style="margin-top: 30px; color: #94a3b8;">This test page works without database connection.</p>
        </div>
    </body>
    </html>
    """.replace("{{ timestamp }}", str(__import__('datetime').datetime.now()))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Enhanced login page with database support"""
    print(f"Login route accessed - Method: {request.method}")
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        print(f"POST data received - Email: '{email}', Password: '{password}'")
        print(f"Form data: {dict(request.form)}")
        
        # First try database authentication if available
        db_status, db_message = test_database_connection()
        if db_status:
            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT user_id, username, role, password, author, genre FROM user_table WHERE email=%s", (email,))
                user = cur.fetchone()
                cur.close()
                
                if user and user[3] == password:
                    session['loggedin'] = True
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = user[2]
                    session['preferred_author'] = user[4]
                    session['preferred_genre'] = user[5]

                    flash(f"Welcome, {session['username']}! (Database mode)", "success")
                    print(f"Database login successful for user: {session['username']}, role: {session['role']}")

                    # Admin users go directly to admin page
                    if session['role'] == 'admin':
                        return redirect(url_for("admin_home"))
                    
                    # Regular users need to set preferences if not set
                    if not user[4] or not user[5]:
                        flash("Please set your author and genre preferences to continue.", "info")
                        return redirect(url_for("preferences"))

                    return redirect(url_for("user_home"))
                    
            except Exception as e:
                print(f"Database authentication error: {e}")
        
        # Fallback to test credentials
        if email == "admin@bookbot.com" and password == "admin123":
            session['loggedin'] = True
            session['user_id'] = 1
            session['username'] = "Admin"
            session['role'] = "admin"
            session['preferred_author'] = "William Shakespeare"
            session['preferred_genre'] = "Fiction"
            flash("Welcome, Admin! (Test mode - no database)", "success")
            print("Test admin login successful - redirecting")
            return redirect(url_for("admin_home"))
        elif email == "user@test.com" and password == "user123":
            session['loggedin'] = True
            session['user_id'] = 2
            session['username'] = "Test User"
            session['role'] = "user"
            session['preferred_author'] = "Jane Austen"
            session['preferred_genre'] = "Romance"
            flash("Welcome, Test User! (Test mode - no database)", "success")
            print("Test user login successful - redirecting")
            return redirect(url_for("user_home"))
        else:
            print(f"Login failed for email: {email}")
            if db_status:
                flash("Invalid email or password.", "error")
            else:
                flash("Invalid credentials. Try admin@bookbot.com/admin123 or user@test.com/user123 (Test mode)", "error")
    
    print("Rendering login template")
    return render_template("login.html")

@app.route("/admin_test")
def admin_test():
    """Test admin page"""
    if 'loggedin' not in session or session.get('role') != 'admin':
        flash("Please log in as admin", "error")
        return redirect(url_for('login'))
    
    return f"""
    <html>
    <head><title>Admin Test</title>
    <style>body{{background:#1e293b;color:white;padding:40px;font-family:Arial;}}</style>
    </head>
    <body>
    <h1>🔧 Admin Test Page</h1>
    <p>Welcome, {session.get('username')}!</p>
    <p>✅ Admin authentication working</p>
    <a href="/logout" style="color:#7c3aed;">Logout</a>
    </body>
    </html>
    """

@app.route("/user_test")
def user_test():
    """Test user page"""
    if 'loggedin' not in session or session.get('role') != 'user':
        flash("Please log in as user", "error")
        return redirect(url_for('login'))
    
    return f"""
    <html>
    <head><title>User Test</title>
    <style>body{{background:#1e293b;color:white;padding:40px;font-family:Arial;}}</style>
    </head>
    <body>
    <h1>👤 User Test Page</h1>
    <p>Welcome, {session.get('username')}!</p>
    <p>✅ User authentication working</p>
    <a href="/logout" style="color:#7c3aed;">Logout</a>
    </body>
    </html>
    """

@app.route("/register", methods=["GET", "POST"])
def register():
    """Basic registration page without database"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        flash(f"Registration successful for {username}! (Test mode - no database)", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/admin_home")
def admin_home():
    """Admin home page"""
    if 'loggedin' not in session or session.get('role') != 'admin':
        flash("Please log in as admin", "error")
        return redirect(url_for('login'))
    
    return render_template('admin.html', username=session['username'])

@app.route("/user_home")
def user_home():
    """User home page"""
    if 'loggedin' not in session or session.get('role') != 'user':
        flash("Please log in as user", "error")
        return redirect(url_for('login'))
    
    return render_template('user.html', username=session['username'])

# Book Management Routes
@app.route("/view_books")
def view_books():
    """View all books (Admin only)"""
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    # Check database connection first
    db_status, db_message = test_database_connection()
    if not db_status:
        flash(f"Database connection error: {db_message}", "error")
        return redirect(url_for('admin_home'))
    
    try:
        books_list = []
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT book_id, title, author, genre, ISBN FROM book_table ORDER BY book_id DESC")
        books_data = cur.fetchall()
        cur.close()
        
        for book in books_data:
            book_info = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4]
            }
            books_list.append(book_info)
        
        return render_template('viewbook.html', books=books_list)
        
    except Exception as e:
        flash(f"An error occurred while fetching books data: {e}", "error")
        return redirect(url_for('admin_home'))

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Add Book (Admin only)"""
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    if request.method == "POST":
        book_title = request.form.get("book_title", "").strip()
        author_name = request.form.get("author_name", "").strip()
        isbn = request.form.get("isbn", "").strip()
        genre = request.form.get("genre", "").strip()
        
        # Validation
        if not all([book_title, author_name, isbn, genre]):
            flash("Please fill out all fields.", "error")
            return render_template("addbook.html")
            
        if len(book_title) < 2:
            flash("Book title must be at least 2 characters long.", "error")
            return render_template("addbook.html")
            
        if len(author_name) < 2:
            flash("Author name must be at least 2 characters long.", "error")
            return render_template("addbook.html")
            
        if len(isbn) < 10:
            flash("ISBN must be at least 10 characters long.", "error")
            return render_template("addbook.html")
        
        # Check database connection
        db_status, db_message = test_database_connection()
        if not db_status:
            flash(f"Database connection error: {db_message}", "error")
            return render_template("addbook.html")
        
        try:
            # Check if book already exists (by title and author or by ISBN)
            cur = mysql.connection.cursor()
            
            # Check for duplicate by title and author
            cur.execute(
                "SELECT book_id FROM book_table WHERE LOWER(title) = %s AND LOWER(author) = %s",
                (book_title.lower(), author_name.lower())
            )
            title_author_exists = cur.fetchone()
            
            # Check for duplicate by ISBN
            cur.execute(
                "SELECT book_id FROM book_table WHERE ISBN = %s",
                (isbn,)
            )
            isbn_exists = cur.fetchone()
            
            if title_author_exists or isbn_exists:
                cur.close()
                flash(f"Book '{book_title}' by {author_name} or ISBN {isbn} already exists in the catalog.", "error")
                return render_template("addbook.html")
            
            # Add new book to database
            cur.execute(
                "INSERT INTO book_table (title, author, genre, ISBN) VALUES (%s, %s, %s, %s)",
                (book_title, author_name, genre, isbn)
            )
            mysql.connection.commit()
            cur.close()
            
            flash(f"Book '{book_title}' by {author_name} has been successfully added to the catalog!", "success")
            return redirect(url_for('view_books'))
            
        except Exception as e:
            flash(f"An error occurred while adding the book: {e}", "error")
            return render_template("addbook.html")
    
    # GET request - display the form
    return render_template("addbook.html")

@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    """Preferences page for users"""
    if 'loggedin' not in session:
        flash("Please log in to set your preferences.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        author_preference = request.form.get("author")
        genre_preference = request.form.get("genre")

        if not author_preference or not genre_preference:
            flash("Please select one author and one genre to continue.", "error")
            return redirect(url_for("preferences"))

        # In test mode, just update session
        session['preferred_author'] = author_preference
        session['preferred_genre'] = genre_preference
        
        flash("Your preferences have been saved!", "success")
        return redirect(url_for("user_home"))
            
    # Fetch authors and genres from database or provide defaults
    db_status, db_message = test_database_connection()
    if db_status:
        try:
            cur = mysql.connection.cursor()
            
            # Get unique authors from book_table
            cur.execute("SELECT DISTINCT author FROM book_table ORDER BY author ASC")
            authors_data = cur.fetchall()
            authors_list = [author[0] for author in authors_data]
            
            # Get unique genres from book_table
            cur.execute("SELECT DISTINCT genre FROM book_table ORDER BY genre ASC")
            genres_data = cur.fetchall()
            genres_list = [genre[0] for genre in genres_data]
            
            cur.close()
            
        except Exception as e:
            # Fallback to default lists if database fails
            authors_list = ['William Shakespeare', 'Jane Austen', 'Charles Dickens', 'Leo Tolstoy', 'Mark Twain']
            genres_list = ['Fiction', 'Romance', 'Mystery', 'Science Fiction', 'Biography']
            flash(f"Using default preferences due to database error: {e}", "warning")
    else:
        # Default lists when database is not available
        authors_list = ['William Shakespeare', 'Jane Austen', 'Charles Dickens', 'Leo Tolstoy', 'Mark Twain']
        genres_list = ['Fiction', 'Romance', 'Mystery', 'Science Fiction', 'Biography']
        flash("Using default preferences (database not available)", "info")
        
    return render_template("preference.html", authors=authors_list, genres=genres_list)

@app.route("/recommended_books")
def recommended_books():
    """Recommended books based on user preferences"""
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    # Get user preferences from session (in test mode)
    preferred_author = session.get('preferred_author')
    preferred_genre = session.get('preferred_genre')
    
    # Check database connection
    db_status, db_message = test_database_connection()
    recommended_books_list = []
    
    if db_status:
        try:
            cur = mysql.connection.cursor()
            
            # First, check if we have any books at all
            cur.execute("SELECT COUNT(*) FROM book_table")
            total_books = cur.fetchone()[0]
            
            if total_books == 0:
                books_data = []
            elif preferred_author and preferred_genre:
                # First try: books that match both user's preferred author AND genre
                query = """
                    SELECT book_id, title, author, genre, ISBN 
                    FROM book_table 
                    WHERE LOWER(author) LIKE LOWER(%s) AND LOWER(genre) LIKE LOWER(%s)
                    ORDER BY title ASC
                    LIMIT 10
                """
                author_pattern = f"%{preferred_author}%"
                genre_pattern = f"%{preferred_genre}%"
                
                cur.execute(query, (author_pattern, genre_pattern))
                books_data = cur.fetchall()
                
                # If no books match both criteria, try author OR genre
                if not books_data:
                    query = """
                        SELECT book_id, title, author, genre, ISBN 
                        FROM book_table 
                        WHERE LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s)
                        ORDER BY title ASC
                        LIMIT 10
                    """
                    cur.execute(query, (author_pattern, genre_pattern))
                    books_data = cur.fetchall()
                    
            else:
                # If no preferences, show recent books
                cur.execute(
                    "SELECT book_id, title, author, genre, ISBN FROM book_table ORDER BY book_id DESC LIMIT 10"
                )
                books_data = cur.fetchall()
            
            cur.close()
            
            # Convert to list of dictionaries and add consistent ratings
            for book in books_data:
                # Generate consistent rating based on book properties
                rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35  # Range 35-49
                rating = round(rating_seed / 10.0, 1)  # Convert to 3.5-4.9 range
                stars = "★" * int(rating) + "☆" * (5 - int(rating))
                
                book_info = {
                    'id': book[0],
                    'title': book[1],
                    'author': book[2],
                    'genre': book[3],
                    'isbn': book[4],
                    'rating': rating,
                    'stars': stars
                }
                recommended_books_list.append(book_info)
                
        except Exception as e:
            flash(f"Error loading recommendations: {e}", "error")
    else:
        flash("Database not available. Please contact administrator.", "error")
    
    return render_template('recommendedbooks.html', 
                           preferred_author=preferred_author, 
                           preferred_genre=preferred_genre,
                           books=recommended_books_list)

@app.route("/setup_database")
def setup_database():
    """Setup database tables if they don't exist"""
    if mysql is None:
        return "MySQL not initialized. Please check configuration."
        
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
        
        # Create book_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS book_table (
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
                FOREIGN KEY (book_id) REFERENCES book_table(book_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_book (user_id, book_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        mysql.connection.commit()
        cur.close()
        
        return f"Database tables created successfully! <a href='{url_for('create_admin')}'>→ Create Admin</a> | <a href='{url_for('populate_sample_books')}'>→ Add Sample Books</a>"
        
    except Exception as e:
        return f"Error setting up database: {e}"

@app.route("/populate_sample_books")
def populate_sample_books():
    """Populate sample books if database is empty"""
    if 'loggedin' not in session:
        return "Please log in first"
    
    if mysql is None:
        return "Database not available"
    
    try:
        cur = mysql.connection.cursor()
        
        # Check if books already exist
        cur.execute("SELECT COUNT(*) FROM book_table")
        book_count = cur.fetchone()[0]
        
        if book_count > 0:
            cur.close()
            return f"Database already has {book_count} books. <a href='{url_for('view_books')}'>View Books</a>"
        
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
                "INSERT INTO book_table (title, author, genre, ISBN) VALUES (%s, %s, %s, %s)",
                book
            )
        
        mysql.connection.commit()
        cur.close()
        
        return f"Successfully added {len(sample_books)} sample books to the database! <a href='{url_for('recommended_books')}'>Go to Recommendations</a> | <a href='{url_for('view_books')}'>View Books</a>"
        
    except Exception as e:
        return f"Error adding sample books: {e}"
@app.route("/create_admin")
def create_admin():
    """Create admin user for testing"""
    if mysql is None:
        return """
        <div style="padding: 2rem; background: #1e293b; color: white; font-family: Arial;">
            <h2>✅ Test Admin Account Available!</h2>
            <div style="background: #0f172a; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <h3>Test Login Credentials (No Database):</h3>
                <p><strong>Email:</strong> admin@bookbot.com</p>
                <p><strong>Password:</strong> admin123</p>
                <p style="color: #f59e0b;"><strong>Note:</strong> Database not available - using test mode!</p>
            </div>
            <a href="/login" style="background: #7c3aed; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 6px;">🔑 Go to Login</a>
        </div>
        """
    
    try:
        cur = mysql.connection.cursor()
        
        # Check if admin already exists
        cur.execute("SELECT user_id FROM user_table WHERE role = 'admin'")
        admin_exists = cur.fetchone()
        
        if admin_exists:
            cur.close()
            return """
            <div style="padding: 2rem; background: #1e293b; color: white; font-family: Arial;">
                <h2>✅ Admin Account Already Exists!</h2>
                <div style="background: #0f172a; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <h3>Use existing admin credentials to login</h3>
                    <p style="color: #10b981;">Admin account is already set up in the database.</p>
                </div>
                <a href="/login" style="background: #7c3aed; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 6px;">🔑 Go to Login</a>
            </div>
            """
        
        # Create default admin user
        admin_data = (
            'Admin',  # username
            'admin123',  # password
            'admin@bookbot.com',  # email
            '9999999999',  # phone
            '1990-01-01',  # dob
            'Other',  # gender
            'admin',  # role
            'William Shakespeare',  # preferred author
            'Fiction'  # preferred genre
        )
        
        cur.execute(
            """INSERT INTO user_table 
               (username, password, email, phone_no, dob, gender, role, author, genre) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            admin_data
        )
        mysql.connection.commit()
        cur.close()
        
        return '''
        <div style="padding: 2rem; background: #1e293b; color: white; font-family: Arial;">
            <h2 style="color: #10b981;">✅ Admin Account Created Successfully!</h2>
            <div style="background: #0f172a; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #3b82f6;">
                <h3>Admin Login Credentials:</h3>
                <p><strong>Email:</strong> admin@bookbot.com</p>
                <p><strong>Password:</strong> admin123</p>
                <p style="color: #dc2626; font-size: 0.9em;"><strong>⚠️ Important:</strong> Please change the password after first login for security!</p>
            </div>
            <div style="margin-top: 2rem;">
                <a href="{}" style="background: #3b82f6; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 6px; display: inline-block;">🔑 Go to Login</a>
            </div>
        </div>
        '''.format(url_for('login'))
        
    except Exception as e:
        return f"Error creating admin user: {e}. <a href='{url_for('login')}'>Go to Login</a>"

# View Registered Users (Admin only)
@app.route("/view_registered_users")
def view_registered_users():
    """View all registered users (Admin only)"""
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    # Check database connection first
    db_status, db_message = test_database_connection()
    if not db_status:
        flash(f"Database connection error: {db_message}", "error")
        return redirect(url_for('admin_home'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT user_id, username, email, phone_no, dob, gender, author, genre FROM user_table WHERE role = 'user' ORDER BY user_id DESC"
        )
        users_data = cur.fetchall()
        cur.close()
        
        users_list = []
        for user in users_data:
            user_info = {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'phone_number': user[3],
                'dob': user[4],
                'gender': user[5],
                'preferred_author': user[6],
                'preferred_genre': user[7]
            }
            users_list.append(user_info)
        
        return render_template('reguser.html', users=users_list)
        
    except Exception as e:
        flash(f"An error occurred while fetching users data: {e}", "error")
        return redirect(url_for('admin_home'))

# Book Search (Global)
@app.route("/search_books", methods=["GET", "POST"])
def search_books():
    """Search books functionality"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    books_list = []
    
    if search_query:
        # Check database connection
        db_status, db_message = test_database_connection()
        if db_status:
            try:
                cur = mysql.connection.cursor()
                # Search in title, author, genre, and ISBN
                search_pattern = f"%{search_query}%"
                cur.execute(
                    """SELECT book_id, title, author, genre, ISBN 
                       FROM book_table 
                       WHERE LOWER(title) LIKE LOWER(%s) 
                          OR LOWER(author) LIKE LOWER(%s) 
                          OR LOWER(genre) LIKE LOWER(%s) 
                          OR LOWER(ISBN) LIKE LOWER(%s)
                       ORDER BY title ASC
                       LIMIT 50""",
                    (search_pattern, search_pattern, search_pattern, search_pattern)
                )
                books_data = cur.fetchall()
                cur.close()
                
                for book in books_data:
                    book_info = {
                        'id': book[0],
                        'title': book[1],
                        'author': book[2],
                        'genre': book[3],
                        'isbn': book[4]
                    }
                    books_list.append(book_info)
                    
            except Exception as e:
                flash(f"An error occurred while searching: {e}", "error")
        else:
            flash("Database not available for search", "error")
    
    return render_template('search_results.html', books=books_list, query=search_query)
def logout():
    """Simple logout"""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    print("Starting minimal Flask application...")
    app.run(debug=True, host='127.0.0.1', port=5000)