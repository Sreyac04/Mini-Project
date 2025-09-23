from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import re
import csv
import os # It's good practice to use os.path.join for cross-platform compatibility

app = Flask(__name__, template_folder="app/templates")
app.secret_key = "your_secret_key_here_please_change_this"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_engine'

mysql = MySQL(app)

# --- Helper Function to Read CSV ---
def read_csv(filename):
    """Reads a single-column CSV file and returns a list of its items."""
    items = []
    try:
        with open(filename, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader)  # Skip header row
            for row in reader:
                if row: # Ensure row is not empty
                    items.append(row[0])
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    return items


# --- Routes ---

# Landing Page
@app.route("/")
def landing():
    if 'loggedin' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_home'))
        else:
            return redirect(url_for('user_home'))
    return render_template("landing.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, username, role, password, author, genre FROM user_table WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and user[3] == password:
            session['loggedin'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            user_author_preference = user[4]
            user_genre_preference = user[5]

            flash(f"Welcome, {session['username']}!", "success")

            # Admin users go directly to admin page
            if session['role'] == 'admin':
                return redirect(url_for("admin_home"))
            
            # Regular users need to set preferences first
            if user_author_preference is None or user_genre_preference is None:
                flash("Please set your author and genre preferences to continue.", "info")
                return redirect(url_for("preferences"))

            return redirect(url_for("user_home"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        dob = request.form.get("dob")
        gender = request.form.get("gender")

        if not all([username, password, email, phone_number, dob, gender]):
            flash("Please fill out all fields.", "error")
            return render_template("register.html")

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """INSERT INTO user_table 
                   (username, password, email, phone_no, dob, gender, role, author, genre) 
                   VALUES (%s, %s, %s, %s, %s, %s, 'user', NULL, NULL)""",
                (username, password, email, phone_number, dob, gender)
            )
            mysql.connection.commit()
            cur.close()
            
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")

# Preferences Page
@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if 'loggedin' not in session:
        flash("Please log in to set your preferences.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        author_preference = request.form.get("author")
        genre_preference = request.form.get("genre")

        if not author_preference or not genre_preference:
            flash("Please select one author and one genre to continue.", "error")
            return redirect(url_for("preferences"))

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE user_table SET author = %s, genre = %s WHERE user_id = %s",
                (author_preference, genre_preference, session['user_id'])
            )
            mysql.connection.commit()
            cur.close()
            
            flash("Your preferences have been saved!", "success")
            return redirect(url_for("user_home"))

        except Exception as e:
            flash(f"An error occurred while saving preferences: {e}", "error")
            return redirect(url_for("preferences"))
            
    # Fetch authors and genres from database
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
        
        return render_template("preference.html", authors=authors_list, genres=genres_list)
        
    except Exception as e:
        flash(f"Error loading preferences data: {e}", "error")
        return render_template("preference.html", authors=[], genres=[])

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# User Home
@app.route("/user_home")
def user_home():
    if 'loggedin' in session and session['role'] == 'user':
        return render_template("user.html", username=session['username'])
    flash("Please log in to access this page.", "error")
    return redirect(url_for('login'))

# Admin Home
@app.route("/admin_home")
def admin_home():
    if 'loggedin' in session and session['role'] == 'admin':
        return render_template('admin.html', username=session['username'])
    flash("You do not have permission to access this page.", "error")
    return redirect(url_for('login'))

# User Profile
@app.route("/profile")
def profile():
    if 'loggedin' not in session:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT username, email, phone_no, dob, gender, author, genre FROM user_table WHERE user_id = %s",
            (session['user_id'],)
        )
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            user_info = {
                'username': user_data[0],
                'email': user_data[1],
                'phone_number': user_data[2],
                'dob': user_data[3],
                'gender': user_data[4],
                'preferred_author': user_data[5],
                'preferred_genre': user_data[6]
            }
            return render_template('profile.html', user=user_info)
        else:
            flash("User data not found.", "error")
            return redirect(url_for('user_home'))
            
    except Exception as e:
        flash(f"An error occurred while fetching profile data: {e}", "error")
        return redirect(url_for('user_home'))

# Edit Profile
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if 'loggedin' not in session:
        flash("Please log in to edit your profile.", "error")
        return redirect(url_for('login'))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        preferred_author = request.form.get("preferred_author", "").strip()
        preferred_genre = request.form.get("preferred_genre", "").strip()
        
        # Validation
        if not all([username, email, phone_number, dob, gender]):
            flash("Please fill out all required fields.", "error")
            return redirect(url_for('edit_profile'))
            
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """UPDATE user_table SET 
                   username = %s, email = %s, phone_no = %s, dob = %s, 
                   gender = %s, author = %s, genre = %s 
                   WHERE user_id = %s""",
                (username, email, phone_number, dob, gender, 
                 preferred_author if preferred_author else None,
                 preferred_genre if preferred_genre else None,
                 session['user_id'])
            )
            mysql.connection.commit()
            cur.close()
            
            # Update session username if it changed
            session['username'] = username
            
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))
            
        except Exception as e:
            flash(f"An error occurred while updating profile: {e}", "error")
            return redirect(url_for('edit_profile'))
    
    # GET request - fetch current user data and preferences
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT username, email, phone_no, dob, gender, author, genre FROM user_table WHERE user_id = %s",
            (session['user_id'],)
        )
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            user_info = {
                'username': user_data[0],
                'email': user_data[1],
                'phone_number': user_data[2],
                'dob': user_data[3],
                'gender': user_data[4],
                'preferred_author': user_data[5],
                'preferred_genre': user_data[6]
            }
            
            # Get authors and genres lists from database for dropdowns
            cur_prefs = mysql.connection.cursor()
            
            # Get unique authors from book_table
            cur_prefs.execute("SELECT DISTINCT author FROM book_table ORDER BY author ASC")
            authors_data = cur_prefs.fetchall()
            authors_list = [author[0] for author in authors_data]
            
            # Get unique genres from book_table
            cur_prefs.execute("SELECT DISTINCT genre FROM book_table ORDER BY genre ASC")
            genres_data = cur_prefs.fetchall()
            genres_list = [genre[0] for genre in genres_data]
            
            cur_prefs.close()
            
            return render_template('editprofile.html', user=user_info, authors=authors_list, genres=genres_list)
        else:
            flash("User data not found.", "error")
            return redirect(url_for('user_home'))
            
    except Exception as e:
        flash(f"An error occurred while fetching profile data: {e}", "error")
        return redirect(url_for('user_home'))

# View Registered Users (Admin only)
@app.route("/view_registered_users")
def view_registered_users():
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
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

# View Books (Admin only)
@app.route("/view_books")
def view_books():
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        # Read books from database
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

# Add Book (Admin only)
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
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

# Book Search (Global)
@app.route("/search_books", methods=["GET", "POST"])
def search_books():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    books_list = []
    
    if search_query:
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
    
    return render_template('search_results.html', books=books_list, query=search_query)

# Recommended Books
@app.route("/recommended_books")
def recommended_books():
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    # Get user preferences for personalized recommendations
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT author, genre FROM user_table WHERE user_id = %s",
            (session['user_id'],)
        )
        user_data = cur.fetchone()
        
        preferred_author = user_data[0] if user_data else None
        preferred_genre = user_data[1] if user_data else None
        
        # Get recommended books based on user preferences
        recommended_books_list = []
        
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
                
        elif preferred_author or preferred_genre:
            # Query books that match user's preferred author or genre
            query = """
                SELECT book_id, title, author, genre, ISBN 
                FROM book_table 
                WHERE LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s)
                ORDER BY title ASC
                LIMIT 10
            """
            author_pattern = f"%{preferred_author}%" if preferred_author else "%"
            genre_pattern = f"%{preferred_genre}%" if preferred_genre else "%"
            
            cur.execute(query, (author_pattern, genre_pattern))
            books_data = cur.fetchall()
        else:
            # If no preferences, show random popular books
            cur.execute(
                "SELECT book_id, title, author, genre, ISBN FROM book_table ORDER BY book_id DESC LIMIT 10"
            )
            books_data = cur.fetchall()
            
        # If still no books found, get any available books
        if not books_data and total_books > 0:
            cur.execute(
                "SELECT book_id, title, author, genre, ISBN FROM book_table ORDER BY book_id DESC LIMIT 10"
            )
            books_data = cur.fetchall()
        
        cur.close()
        
        # Convert to list of dictionaries and add consistent ratings
        for book in books_data:
            # Generate consistent rating based on book properties (not random)
            # Use book_id and title length for deterministic rating
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
        preferred_author = None
        preferred_genre = None
        recommended_books_list = []
        flash(f"Error loading recommendations: {e}", "error")
    
    return render_template('recommendedbooks.html', 
                           preferred_author=preferred_author, 
                           preferred_genre=preferred_genre,
                           books=recommended_books_list)

# Recently Rated Books
@app.route("/recently_rated")
def recently_rated():
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    return render_template('recently_rated.html', username=session['username'])

# Favorites
@app.route("/favorites")
def favorites():
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # Get user's favorite books using existing table
        cur.execute(
            """SELECT f.fav_id, b.book_id, b.title, b.author, b.genre, b.ISBN 
               FROM favorite_book_table f 
               JOIN book_table b ON f.book_id = b.book_id 
               WHERE f.user_id = %s 
               ORDER BY f.fav_id DESC""",
            (session['user_id'],)
        )
        favorites_data = cur.fetchall()
        cur.close()
        
        favorites_list = []
        for fav in favorites_data:
            # Generate consistent rating for each book
            rating_seed = (fav[1] * 7 + len(fav[2])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            
            book_info = {
                'fav_id': fav[0],
                'id': fav[1],
                'title': fav[2],
                'author': fav[3],
                'genre': fav[4],
                'isbn': fav[5],
                'rating': rating,
                'stars': stars
            }
            favorites_list.append(book_info)
        
        return render_template('favorites.html', favorites=favorites_list, username=session['username'])
        
    except Exception as e:
        flash(f"Error loading favorites: {e}", "error")
        return render_template('favorites.html', favorites=[], username=session['username'])

# Add to Favorites
@app.route("/add_to_favorites/<int:book_id>", methods=["POST"])
def add_to_favorites(book_id):
    if 'loggedin' not in session:
        return {'success': False, 'message': 'Please log in'}, 401
    
    try:
        cur = mysql.connection.cursor()
        
        # Check if book exists
        cur.execute("SELECT book_id FROM book_table WHERE book_id = %s", (book_id,))
        if not cur.fetchone():
            cur.close()
            return {'success': False, 'message': 'Book not found'}, 404
        
        # Check if already in favorites using existing table
        cur.execute(
            "SELECT fav_id FROM favorite_book_table WHERE user_id = %s AND book_id = %s",
            (session['user_id'], book_id)
        )
        if cur.fetchone():
            cur.close()
            return {'success': False, 'message': 'Book already in favorites'}, 400
        
        # Add to favorites using existing table
        cur.execute(
            "INSERT INTO favorite_book_table (user_id, book_id) VALUES (%s, %s)",
            (session['user_id'], book_id)
        )
        mysql.connection.commit()
        cur.close()
        
        return {'success': True, 'message': 'Book added to favorites'}
        
    except Exception as e:
        return {'success': False, 'message': f'Error: {e}'}, 500

# Remove from Favorites
@app.route("/remove_from_favorites/<int:fav_id>", methods=["POST"])
def remove_from_favorites(fav_id):
    if 'loggedin' not in session:
        return {'success': False, 'message': 'Please log in'}, 401
    
    try:
        cur = mysql.connection.cursor()
        
        # Remove from favorites using existing table (ensure it belongs to the current user)
        cur.execute(
            "DELETE FROM favorite_book_table WHERE fav_id = %s AND user_id = %s",
            (fav_id, session['user_id'])
        )
        mysql.connection.commit()
        
        if cur.rowcount > 0:
            cur.close()
            return {'success': True, 'message': 'Book removed from favorites'}
        else:
            cur.close()
            return {'success': False, 'message': 'Favorite not found'}, 404
            
    except Exception as e:
        return {'success': False, 'message': f'Error: {e}'}, 500

# Continue Reading
@app.route("/continue_reading")
def continue_reading():
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    return render_template('continue_reading.html', username=session['username'])

# Book Details
@app.route("/book/<int:book_id>")
def book_details(book_id):
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT book_id, title, author, genre, ISBN FROM book_table WHERE book_id = %s",
            (book_id,)
        )
        book_data = cur.fetchone()
        cur.close()
        
        if book_data:
            # Generate consistent rating based on book properties (same logic as recommended_books)
            rating_seed = (book_data[0] * 7 + len(book_data[1])) % 15 + 35  # Range 35-49
            rating = round(rating_seed / 10.0, 1)  # Convert to 3.5-4.9 range
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            
            # Generate a short description based on book title
            title_descriptions = {
                'Romeo and Juliet': 'A timeless tale of young love and tragic fate. Shakespeare\'s masterpiece tells the story of two star-crossed lovers from feuding families in Verona, whose passionate romance ultimately leads to reconciliation between their warring houses.',
                'War and Peace': 'Tolstoy\'s epic novel follows the lives of Russian aristocrats during the Napoleonic era. A sweeping narrative that explores themes of love, war, faith, and the meaning of history through the interconnected stories of several families.',
                'Pride and Prejudice': 'Jane Austen\'s beloved romance follows Elizabeth Bennet as she navigates love, family, and social expectations in 19th-century England. A witty exploration of marriage, morality, and the importance of looking beyond first impressions.',
                'To Kill a Mockingbird': 'Harper Lee\'s powerful novel addresses racial injustice through the eyes of young Scout Finch in Depression-era Alabama. A coming-of-age story that examines moral courage and the loss of innocence.',
                'The Great Gatsby': 'F. Scott Fitzgerald\'s masterpiece captures the decadence and disillusionment of the Jazz Age. The story of Jay Gatsby\'s obsessive pursuit of the American Dream and lost love in the glittering world of 1920s New York.',
                'Jane Eyre': 'Charlotte Brontë\'s Gothic romance follows an orphaned governess who finds love and independence. A groundbreaking novel that explores themes of class, sexuality, and women\'s equality in Victorian society.',
                'Wuthering Heights': 'Emily Brontë\'s dark and passionate tale of obsessive love between Heathcliff and Catherine. Set on the Yorkshire moors, this Gothic novel explores themes of revenge, social class, and the destructive nature of consuming passion.',
                'The Catcher in the Rye': 'J.D. Salinger\'s coming-of-age novel follows teenager Holden Caulfield as he wanders New York City. A frank exploration of adolescent alienation, identity, and the loss of innocence in post-war America.',
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

if __name__ == "__main__":
    app.run(debug=True)

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
        cur.execute("SELECT COUNT(*) FROM book_table")
        total_books = cur.fetchone()[0]
        
        # Get sample books
        cur.execute("SELECT book_id, title, author, genre FROM book_table LIMIT 5")
        sample_books = cur.fetchall()
        
        # Get all unique authors and genres
        cur.execute("SELECT DISTINCT author FROM book_table ORDER BY author")
        authors = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT DISTINCT genre FROM book_table ORDER BY genre")
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

# Route to populate sample books if database is empty
@app.route("/populate_sample_books")
def populate_sample_books():
    if 'loggedin' not in session:
        return "Please log in first"
    
    try:
        cur = mysql.connection.cursor()
        
        # Check if books already exist
        cur.execute("SELECT COUNT(*) FROM book_table")
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
                "INSERT INTO book_table (title, author, genre, ISBN) VALUES (%s, %s, %s, %s)",
                book
            )
        
        mysql.connection.commit()
        cur.close()
        
        return f"Successfully added {len(sample_books)} sample books to the database! <a href='{url_for('recommended_books')}'>Go to Recommendations</a> | <a href='{url_for('debug_db')}'>View Debug Info</a>"
        
    except Exception as e:
        return f"Error adding sample books: {e}"