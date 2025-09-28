from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
import re
import csv
import os # It's good practice to use os.path.join for cross-platform compatibility
import socket

app = Flask(__name__, template_folder="app/templates")
app.secret_key = "your_secret_key_here_please_change_this"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_engine'
app.config['MYSQL_CONNECT_TIMEOUT'] = 5

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
        
        # Get unique authors from new_book_table
        cur.execute("SELECT DISTINCT author FROM new_book_table ORDER BY author ASC")
        authors_data = cur.fetchall()
        authors_list = [author[0] for author in authors_data]
        
        # Get unique genres from new_book_table
        cur.execute("SELECT DISTINCT genre FROM new_book_table ORDER BY genre ASC")
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
        phone_number = request.form.get("phone_number", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        preferred_author = request.form.get("preferred_author", "").strip()
        preferred_genre = request.form.get("preferred_genre", "").strip()
        
        # Validation - email is not required from form since it's read-only
        if not all([username, phone_number, dob, gender]):
            flash("Please fill out all required fields.", "error")
            return redirect(url_for('edit_profile'))
            
        # Get email from database since it's read-only
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT email FROM user_table WHERE user_id = %s", (session['user_id'],))
            email_data = cur.fetchone()
            email = email_data[0] if email_data else ""
            cur.close()
        except Exception as e:
            flash(f"Error retrieving user email: {e}", "error")
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
            
            # Get unique authors from new_book_table
            cur_prefs.execute("SELECT DISTINCT author FROM new_book_table ORDER BY author ASC")
            authors_data = cur_prefs.fetchall()
            authors_list = [author[0] for author in authors_data]
            
            # Get unique genres from new_book_table
            cur_prefs.execute("SELECT DISTINCT genre FROM new_book_table ORDER BY genre ASC")
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
        
        # Organize users by preferred author
        users_by_author = {}
        for user in users_list:
            author = user['preferred_author'] if user['preferred_author'] else 'Not Set'
            if author not in users_by_author:
                users_by_author[author] = []
            users_by_author[author].append(user)
        
        # Organize users by preferred genre
        users_by_genre = {}
        for user in users_list:
            genre = user['preferred_genre'] if user['preferred_genre'] else 'Not Set'
            if genre not in users_by_genre:
                users_by_genre[genre] = []
            users_by_genre[genre].append(user)
        
        # Calculate percentages for authors
        total_users = len(users_list)
        author_stats = {}
        for author, users in users_by_author.items():
            count = len(users)
            percentage = (count / total_users * 100) if total_users > 0 else 0
            author_stats[author] = {
                'count': count,
                'percentage': round(percentage, 1),
                'width': percentage
            }
        
        # Calculate percentages for genres
        genre_stats = {}
        for genre, users in users_by_genre.items():
            count = len(users)
            percentage = (count / total_users * 100) if total_users > 0 else 0
            genre_stats[genre] = {
                'count': count,
                'percentage': round(percentage, 1),
                'width': percentage
            }
        
        # Sort author_stats and genre_stats by count in descending order
        sorted_author_stats = dict(sorted(author_stats.items(), key=lambda item: item[1]['count'], reverse=True))
        sorted_genre_stats = dict(sorted(genre_stats.items(), key=lambda item: item[1]['count'], reverse=True))
        
        return render_template('reguser.html', 
                             users=users_list, 
                             users_by_author=users_by_author, 
                             users_by_genre=users_by_genre,
                             author_stats=sorted_author_stats,
                             genre_stats=sorted_genre_stats,
                             total_users=total_users)
        
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
        cur.execute("SELECT book_id, title, author, genre, ISBN FROM new_book_table ORDER BY book_id DESC")
        books_data = cur.fetchall()
        cur.close()
        
        print(f"DEBUG: Found {len(books_data)} books in database")
        
        for book in books_data:
            book_info = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4]
            }
            books_list.append(book_info)
        
        # Show first 5 books for debugging
        print(f"DEBUG: First 5 books being sent to template:")
        for i, book in enumerate(books_list[:5]):
            print(f"  {i+1}. ID: {book['id']}, Title: '{book['title']}', Author: '{book['author']}'")
        
        print(f"DEBUG: Rendering viewbook.html with {len(books_list)} books")
        
        # Create response with cache-busting headers
        response = render_template('viewbook.html', books=books_list)
        return response
        
    except Exception as e:
        print(f"DEBUG: Error in view_books: {e}")
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
        
        # Debug logging
        print(f"DEBUG: Form data received:")
        print(f"  book_title: '{book_title}'")
        print(f"  author_name: '{author_name}'")
        print(f"  isbn: '{isbn}'")
        print(f"  genre: '{genre}'")
        
        # Validation
        if not all([book_title, author_name, isbn, genre]):
            print(f"DEBUG: Validation failed - missing fields")
            flash("Please fill out all fields.", "error")
            return render_template("addbook.html")
            
        if len(book_title) < 2:
            print(f"DEBUG: Validation failed - book title too short")
            flash("Book title must be at least 2 characters long.", "error")
            return render_template("addbook.html")
            
        if len(author_name) < 2:
            print(f"DEBUG: Validation failed - author name too short")
            flash("Author name must be at least 2 characters long.", "error")
            return render_template("addbook.html")
            
        # Updated ISBN validation - must be exactly 13 digits
        if len(isbn) != 13 or not isbn.isdigit():
            print(f"DEBUG: Validation failed - ISBN must be exactly 13 digits")
            flash("ISBN must contain exactly 13 digits.", "error")
            return render_template("addbook.html")
        
        try:
            # Check if book already exists (by title only)
            cur = mysql.connection.cursor()
            
            # Check for duplicate by title only
            cur.execute(
                "SELECT book_id FROM new_book_table WHERE LOWER(title) = %s",
                (book_title.lower(),)
            )
            title_exists = cur.fetchone()
            
            if title_exists:
                print(f"DEBUG: Duplicate book title found")
                cur.close()
                flash(f"Book '{book_title}' already exists in the catalog.", "error")
                return render_template("addbook.html")
            
            # Add new book to database
            print(f"DEBUG: Adding book to database...")
            cur.execute(
                "INSERT INTO new_book_table (title, author, genre, ISBN) VALUES (%s, %s, %s, %s)",
                (book_title, author_name, genre, isbn)
            )
            mysql.connection.commit()
            book_id = cur.lastrowid
            cur.close()
            
            print(f"DEBUG: Book added successfully with ID: {book_id}")
            flash(f"Book '{book_title}' by {author_name} has been successfully added to the catalog!", "success")
            return redirect(url_for('view_books'))
            
        except Exception as e:
            print(f"DEBUG: Database error: {e}")
            flash(f"An error occurred while adding the book: {e}", "error")
            return render_template("addbook.html")
    
    # GET request - display the form
    return render_template("addbook.html")

# Check for duplicate books (AJAX endpoint) - only check book title
@app.route("/check_duplicate", methods=["POST"])
def check_duplicate():
    """AJAX endpoint to check for duplicate book titles only"""
    if 'loggedin' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        cur = mysql.connection.cursor()
        
        # Check for duplicate by title only
        cur.execute(
            "SELECT book_id FROM new_book_table WHERE LOWER(title) = %s",
            (title.lower(),)
        )
        title_exists = cur.fetchone()
        
        cur.close()
        
        if title_exists:
            return jsonify({'exists': True, 'type': 'title'})
        else:
            return jsonify({'exists': False})
            
    except Exception as e:
        print(f"DEBUG: Error in check_duplicate: {e}")
        return jsonify({'error': str(e)}), 500

# API endpoint for search suggestions
@app.route("/api/search_suggestions")
def search_suggestions():
    if 'loggedin' not in session:
        return {'suggestions': []}
    
    query = request.args.get('q', '').strip()
    suggestions = []
    
    if query and len(query) >= 2:  # Only search if query has at least 2 characters
        try:
            cur = mysql.connection.cursor()
            search_pattern = f"%{query}%"
            
            # Get book suggestions (title, author, genre)
            cur.execute(
                """SELECT DISTINCT title, author, genre, book_id 
                   FROM new_book_table 
                   WHERE LOWER(title) LIKE LOWER(%s) 
                      OR LOWER(author) LIKE LOWER(%s) 
                      OR LOWER(genre) LIKE LOWER(%s)
                   ORDER BY title ASC
                   LIMIT 10""",
                (search_pattern, search_pattern, search_pattern)
            )
            books_data = cur.fetchall()
            cur.close()
            
            for book in books_data:
                suggestions.append({
                    'id': book[3],
                    'title': book[0],
                    'author': book[1],
                    'genre': book[2],
                    'type': 'book'
                })
                
        except Exception as e:
            print(f"Error in search suggestions: {e}")
    
    return jsonify({'suggestions': suggestions})

# Explore Books
@app.route("/explore_by_books")
def explore_by_books():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    books_list = []
    
    try:
        cur = mysql.connection.cursor()
        
        if search_query:
            # Search in title, author, genre, and ISBN
            search_pattern = f"%{search_query}%"
            cur.execute(
                """SELECT book_id, title, author, genre, ISBN 
                   FROM new_book_table 
                   WHERE LOWER(title) LIKE LOWER(%s) 
                      OR LOWER(author) LIKE LOWER(%s) 
                      OR LOWER(genre) LIKE LOWER(%s) 
                      OR LOWER(ISBN) LIKE LOWER(%s)
                   ORDER BY title ASC""",
                (search_pattern, search_pattern, search_pattern, search_pattern)
            )
        else:
            # Get all books from new_book_table
            cur.execute("SELECT book_id, title, author, genre, ISBN FROM new_book_table ORDER BY title ASC")
            
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
        books_list = []
        flash(f"An error occurred while loading books: {e}", "error")
    
    return render_template('explorebybook.html', books=books_list, query=search_query)

# Explore Authors
@app.route("/explore_by_authors")
def explore_by_authors():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # Get all unique authors from new_book_table with book counts
        cur.execute("""
            SELECT author, COUNT(*) as book_count 
            FROM new_book_table 
            GROUP BY author 
            ORDER BY author ASC
        """)
        authors_data = cur.fetchall()
        cur.close()
        
        authors_list = []
        for author in authors_data:
            authors_list.append({
                'name': author[0],
                'book_count': author[1]
            })
            
    except Exception as e:
        authors_list = []
        flash(f"An error occurred while loading authors: {e}", "error")
    
    return render_template('explorebyauthor.html', authors=authors_list)

# Explore Genres
@app.route("/explore_by_genres")
def explore_by_genres():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # Get all unique genres from new_book_table with book counts
        cur.execute("""
            SELECT genre, COUNT(*) as book_count 
            FROM new_book_table 
            GROUP BY genre 
            ORDER BY genre ASC
        """)
        genres_data = cur.fetchall()
        cur.close()
        
        genres_list = []
        for genre in genres_data:
            genres_list.append({
                'name': genre[0],
                'book_count': genre[1]
            })
            
    except Exception as e:
        genres_list = []
        flash(f"An error occurred while loading genres: {e}", "error")
    
    return render_template('explorebygenre.html', genres=genres_list)

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
                   FROM new_book_table 
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
        cur.execute("SELECT COUNT(*) FROM new_book_table")
        total_books = cur.fetchone()[0]
        
        if total_books == 0:
            books_data = []
        elif preferred_author and preferred_genre:
            # First try: books that match both user's preferred author AND genre
            query = """
                SELECT book_id, title, author, genre, ISBN 
                FROM new_book_table 
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
                    FROM new_book_table 
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
                FROM new_book_table 
                WHERE LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s)
                ORDER BY title ASC
                LIMIT 10
            """
            author_pattern = f"%{preferred_author}%" if preferred_author else "%"
            genre_pattern = f"%{preferred_genre}%" if preferred_genre else "%"
            
            cur.execute(query, (author_pattern, genre_pattern))
            books_data = cur.fetchall()
        else:
            # If no preferences, show popular books
            cur.execute(
                "SELECT book_id, title, author, genre, ISBN FROM new_book_table ORDER BY book_id DESC LIMIT 10"
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
               JOIN new_book_table b ON f.book_id = b.book_id 
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
        cur.execute("SELECT book_id FROM new_book_table WHERE book_id = %s", (book_id,))
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
            
            # Generate a short description based on book title
            title_descriptions = {
                'Romeo and Juliet': 'A timeless tale of young love and tragic fate. Shakespeare\'s masterpiece tells the story of two star-crossed lovers from feuding families in Verona, whose passionate romance ultimately leads to reconciliation between their warring houses.',
                'War and Peace': 'Tolstoy\'s epic novel follows the lives of Russian aristocrats during the Napoleonic era. A sweeping narrative that explores themes of love, war, faith, and the meaning of history through the interconnected stories of several families.',
                'Pride and Prejudice': 'Jane Austen\'s beloved romance follows Elizabeth Bennet as she navigates love, family, and social expectations in 19th-century England. A witty exploration of marriage, morality, and the importance of looking beyond first impressions.',
                'To Kill a Mockingbird': 'Harper Lee\'s powerful novel addresses racial injustice through the eyes of young Scout Finch in Depression-era Alabama. A coming-of-age story that examines moral courage and the loss of innocence.',
                'The Great Gatsby': 'F. Scott Fitzgerald\'s masterpiece captures the decadence and disillusionment of the Jazz Age. The story of Jay Gatsby\'s obsessive pursuit of the American Dream and lost love in the glittering world of 1920s New York.',
                'Jane Eyre': 'Charlotte Brontë\'s Gothic romance follows an orphaned governess who finds love and independence. A groundbreaking novel that explores themes of class, sexuality, and women\'s equality in Victorian society.',
                'Wuthering Heights': 'Emily Brontë\'s dark and passionate tale of obsessive love between Heathcliff and Catherine. Set on the Yorkshire moors, this Gothic novel explores themes of revenge, social class, and the destructive nature of consuming passion.',
                'The Catcher in the Rye': 'J.D. Salinger\'s coming-of-age novel follows teenager Holden Caulfield as he wanders New York City. A frank exploration of adolescent alienation, identity, and the loss of innocence