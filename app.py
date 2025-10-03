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
        
        # Get all books for different recommendation types
        trending_books = get_trending_books(cur)
        liked_books = get_liked_books(cur, session['user_id'])
        preference_books = get_preference_based_books(cur, preferred_author, preferred_genre, session['user_id'])
        similar_user_books = get_similar_user_books(cur, session['user_id'])
        content_based_books = get_content_based_books(cur, session['user_id'])
        feedback_books = get_feedback_based_books(cur, session['user_id'])
        
        # Get default recommended books based on user preferences
        recommended_books_list = get_default_recommendations(cur, preferred_author, preferred_genre)
        
        cur.close()
        
    except Exception as e:
        preferred_author = None
        preferred_genre = None
        trending_books = []
        liked_books = []
        preference_books = []
        similar_user_books = []
        content_based_books = []
        feedback_books = []
        recommended_books_list = []
        flash(f"Error loading recommendations: {e}", "error")
    
    return render_template('recommendedbooks.html', 
                           preferred_author=preferred_author, 
                           preferred_genre=preferred_genre,
                           books=recommended_books_list,
                           trending_books=trending_books,
                           liked_books=liked_books,
                           preference_books=preference_books,
                           similar_user_books=similar_user_books,
                           content_based_books=content_based_books,
                           feedback_books=feedback_books)

def get_liked_books(cur, user_id):
    """Get books similar to those the user has previously liked (favorites and highly rated)"""
    try:
        # Get user's favorite books and highly rated books (4+ stars)
        cur.execute("""
            SELECT DISTINCT b.book_id, b.title, b.author, b.genre, b.ISBN
            FROM new_book_table b
            WHERE b.book_id IN (
                SELECT book_id FROM favorite_book_table WHERE user_id = %s
                UNION
                SELECT book_id FROM rating_table WHERE user_id = %s AND rating >= 4
            )
        """, (user_id, user_id))
        
        liked_books_data = cur.fetchall()
        
        if not liked_books_data:
            # If no favorites or highly rated books, get recently rated books
            cur.execute("""
                SELECT DISTINCT b.book_id, b.title, b.author, b.genre, b.ISBN
                FROM new_book_table b
                JOIN rating_table r ON b.book_id = r.book_id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
                LIMIT 5
            """, (user_id,))
            liked_books_data = cur.fetchall()
        
        # Get genres and authors of liked books
        liked_genres = set()
        liked_authors = set()
        
        for book in liked_books_data:
            liked_genres.add(book[3])  # genre
            liked_authors.add(book[2])  # author
        
        if not liked_genres and not liked_authors:
            return []
        
        # Build query for books with similar genres or authors that user hasn't read
        genre_conditions = []
        author_conditions = []
        params = []
        
        for genre in liked_genres:
            genre_conditions.append("LOWER(genre) LIKE LOWER(%s)")
            params.append(f"%{genre}%")
        
        for author in liked_authors:
            author_conditions.append("LOWER(author) LIKE LOWER(%s)")
            params.append(f"%{author}%")
        
        genre_query = " OR ".join(genre_conditions) if genre_conditions else "1=0"
        author_query = " OR ".join(author_conditions) if author_conditions else "1=0"
        
        # Get books with similar genres or authors that user hasn't read
        query = f"""
            SELECT DISTINCT book_id, title, author, genre, ISBN
            FROM new_book_table
            WHERE ({genre_query} OR {author_query})
            AND book_id NOT IN (
                SELECT book_id FROM rating_table WHERE user_id = %s
                UNION
                SELECT book_id FROM favorite_book_table WHERE user_id = %s
            )
            ORDER BY RAND()
            LIMIT 10
        """
        
        params.extend([user_id, user_id])
        cur.execute(query, params)
        books_data = cur.fetchall()
        
        liked_books = []
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            liked_books.append(book_info)
        
        return liked_books
    except Exception as e:
        print(f"Error getting liked books: {e}")
        return []

def get_trending_books(cur):
    """Get highly rated books (trending)"""
    try:
        # Get books with highest average ratings
        cur.execute("""
            SELECT b.book_id, b.title, b.author, b.genre, b.ISBN, 
                   AVG(r.rating) as avg_rating, COUNT(r.rating) as rating_count
            FROM new_book_table b
            JOIN rating_table r ON b.book_id = r.book_id
            GROUP BY b.book_id, b.title, b.author, b.genre, b.ISBN
            HAVING COUNT(r.rating) >= 3  -- Only books with at least 3 ratings
            ORDER BY AVG(r.rating) DESC, COUNT(r.rating) DESC
            LIMIT 10
        """)
        books_data = cur.fetchall()
        
        trending_books = []
        five_star_books = []  # New list for 5-star rated books
        
        for book in books_data:
            # Calculate actual average rating from database
            avg_rating = book[5] if book[5] else 0
            
            # Generate consistent rating based on book properties for display
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            display_rating = round(rating_seed / 10.0, 1)
            stars = "★" * int(display_rating) + "☆" * (5 - int(display_rating))
            
            book_info = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4],
                'rating': display_rating,
                'stars': stars,
                'avg_rating': round(avg_rating, 2),
                'rating_count': book[6]
            }
            
            # Add to trending books
            trending_books.append(book_info)
            
            # If this is a 5-star rated book (avg rating >= 4.5), also add to five_star_books
            if avg_rating >= 4.5:
                five_star_books.append(book_info)
        
        # Prioritize 5-star books in the trending list
        if five_star_books:
            # Combine 5-star books with other trending books, prioritizing 5-star
            # Take up to 5 five-star books and fill the rest with other trending books
            result_books = five_star_books[:5] + [book for book in trending_books if book not in five_star_books][:5]
            return result_books[:10]  # Return maximum 10 books
        else:
            return trending_books[:10]  # Return top 10 trending books
    except Exception as e:
        print(f"Error getting trending books: {e}")
        return []

def get_preference_based_books(cur, preferred_author, preferred_genre, user_id):
    """Get books based on user's preferred author and genre"""
    try:
        recommended_books = []
        
        if preferred_author and preferred_genre:
            # First try: books that match both user's preferred author AND genre
            query = """
                SELECT book_id, title, author, genre, ISBN 
                FROM new_book_table 
                WHERE (LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s))
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
        
        # Convert to list of dictionaries and add consistent ratings
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            
            book_info = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4],
                'rating': rating,
                'stars': stars,
                'avg_rating': round(book[5], 2) if book[5] else 0,
                'rating_count': book[6]
            }
            recommended_books.append(book_info)
        
        return recommended_books
    except Exception as e:
        print(f"Error getting preference-based books: {e}")
        return []

def get_user_ratings(cur, user_id):
    """Get user's ratings"""
    try:
        cur.execute(
            "SELECT book_id, rating FROM rating_table WHERE user_id = %s", (user_id,)
        )
        ratings_data = cur.fetchall()
        user_ratings = {book_id: rating for book_id, rating in ratings_data}
        return user_ratings
    except Exception as e:
        print(f"Error getting user ratings: {e}")
        return {}

def get_book_details(cur, book_id):
    """Get details of a specific book"""
    try:
        cur.execute(
            "SELECT book_id, title, author, genre, ISBN FROM new_book_table WHERE book_id = %s",
            (book_id,),
        )
        book_data = cur.fetchone()
        if book_data:
            book_info = {
                'id': book_data[0],
                'title': book_data[1],
                'author': book_data[2],
                'genre': book_data[3],
                'isbn': book_data[4],
            }
            return book_info
        else:
            return {}
    except Exception as e:
        print(f"Error getting book details: {e}")
        return {}

def get_user_recommendations(cur, user_id):
    """Get book recommendations for a user"""
    try:
        # Get user's ratings
        user_ratings = get_user_ratings(cur, user_id)
        if not user_ratings:
            return []

        # Get all books and their average ratings
        cur.execute("""
            SELECT book_id, title, author, genre, ISBN, 
                   AVG(rating) as avg_rating, COUNT(rating) as rating_count
            FROM new_book_table b
            JOIN rating_table r ON b.book_id = r.book_id
            GROUP BY b.book_id, b.title, b.author, b.genre, b.ISBN
            HAVING COUNT(rating) >= 3  -- Only books with at least 3 ratings
            ORDER BY AVG(rating) DESC, COUNT(rating) DESC
        """)
        books_data = cur.fetchall()

        # Calculate similarity scores for each book
        book_scores = {}
        for book in books_data:
            book_id = book[0]
            if book_id in user_ratings:
                continue  # Skip books the user has already rated

            # Calculate similarity score based on user ratings and book's average rating
            similarity_score = 0
            for rated_book_id, user_rating in user_ratings.items():
                cur.execute(
                    "SELECT AVG(rating) as avg_rating FROM rating_table WHERE book_id = %s",
                    (rated_book_id,),
                )
                avg_rating = cur.fetchone()[0]
                similarity_score += abs(user_rating - avg_rating)

            book_scores[book_id] = similarity_score

        # Sort books by similarity score (ascending) and get top 10 recommendations
        recommended_books = sorted(book_scores, key=book_scores.get)[:10]

        # Fetch details for recommended books
        recommendations = []
        for book_id in recommended_books:
            book_info = get_book_details(cur, book_id)
            if book_info:
                recommendations.append(book_info)

        return recommendations
    except Exception as e:
        print(f"Error getting user recommendations: {e}")
        return []

def get_preference_based_books(cur, preferred_author, preferred_genre, user_id):
    """Get books based on user's preferred author and genre"""
    try:
        recommended_books = []
        
        if preferred_author and preferred_genre:
            # First try: books that match both user's preferred author AND genre
            query = """
                SELECT book_id, title, author, genre, ISBN 
                FROM new_book_table 
                WHERE (LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s))
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
        
        # Convert to list of dictionaries and add consistent ratings
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            recommended_books.append(book_info)
        
        return recommended_books
    except Exception as e:
        print(f"Error getting preference-based books: {e}")
        return []

def get_similar_user_books(cur, user_id):
    """Get books that similar users liked"""
    try:
        # Find users who rated the same books as the current user highly
        cur.execute("""
            SELECT DISTINCT b.book_id, b.title, b.author, b.genre, b.ISBN
            FROM new_book_table b
            JOIN rating_table r ON b.book_id = r.book_id
            WHERE r.user_id IN (
                SELECT DISTINCT r2.user_id
                FROM rating_table r1
                JOIN rating_table r2 ON r1.book_id = r2.book_id
                WHERE r1.user_id = %s AND r1.rating >= 4 AND r2.rating >= 4 AND r2.user_id != %s
            )
            AND b.book_id NOT IN (
                SELECT book_id FROM rating_table WHERE user_id = %s
            )
            ORDER BY RAND()
            LIMIT 10
        """, (user_id, user_id, user_id))
        
        books_data = cur.fetchall()
        
        similar_books = []
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            similar_books.append(book_info)
        
        return similar_books
    except Exception as e:
        print(f"Error getting similar user books: {e}")
        return []

def get_content_based_books(cur, user_id):
    """Get books similar to those the user has favorited or highly rated"""
    try:
        # Get user's favorite books or highly rated books
        cur.execute("""
            SELECT DISTINCT b.genre, b.author
            FROM new_book_table b
            JOIN (
                SELECT book_id FROM favorite_book_table WHERE user_id = %s
                UNION
                SELECT book_id FROM rating_table WHERE user_id = %s AND rating >= 4
            ) user_books ON b.book_id = user_books.book_id
        """, (user_id, user_id))
        
        user_preferences = cur.fetchall()
        
        if not user_preferences:
            # If no favorites or highly rated books, get recently rated books
            cur.execute("""
                SELECT DISTINCT b.genre, b.author
                FROM new_book_table b
                JOIN rating_table r ON b.book_id = r.book_id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
                LIMIT 5
            """, (user_id,))
            user_preferences = cur.fetchall()
        
        if not user_preferences:
            return []
        
        # Build query for books with similar genres or authors
        genre_conditions = []
        author_conditions = []
        params = []
        
        for pref in user_preferences:
            genre_conditions.append("LOWER(genre) LIKE LOWER(%s)")
            author_conditions.append("LOWER(author) LIKE LOWER(%s)")
            params.extend([f"%{pref[0]}%", f"%{pref[1]}%"])
        
        genre_query = " OR ".join(genre_conditions)
        author_query = " OR ".join(author_conditions)
        
        # Get books with similar genres or authors that user hasn't read
        query = f"""
            SELECT DISTINCT book_id, title, author, genre, ISBN
            FROM new_book_table
            WHERE ({genre_query} OR {author_query})
            AND book_id NOT IN (
                SELECT book_id FROM rating_table WHERE user_id = %s
                UNION
                SELECT book_id FROM favorite_book_table WHERE user_id = %s
            )
            ORDER BY RAND()
            LIMIT 10
        """
        
        params.extend([user_id, user_id])
        cur.execute(query, params)
        books_data = cur.fetchall()
        
        content_books = []
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            content_books.append(book_info)
        
        return content_books
    except Exception as e:
        print(f"Error getting content-based books: {e}")
        return []

def get_feedback_based_books(cur, user_id):
    """Get books based on user's feedback"""
    try:
        # Get user's feedback
        cur.execute("""
            SELECT book_id, feedback
            FROM feedback_table
            WHERE user_id = %s
        """, (user_id,))
        
        feedback_data = cur.fetchall()
        
        if not feedback_data:
            return []
        
        # Build query for books with similar feedback
        feedback_conditions = []
        params = []
        
        for feedback in feedback_data:
            feedback_conditions.append("LOWER(feedback) LIKE LOWER(%s)")
            params.append(f"%{feedback[1]}%")
        
        feedback_query = " OR ".join(feedback_conditions)
        
        # Get books with similar feedback that user hasn't read
        query = f"""
            SELECT DISTINCT book_id, title, author, genre, ISBN
            FROM new_book_table
            WHERE {feedback_query}
            AND book_id NOT IN (
                SELECT book_id FROM rating_table WHERE user_id = %s
                UNION
                SELECT book_id FROM favorite_book_table WHERE user_id = %s
            )
            ORDER BY RAND()
            LIMIT 10
        """
        
        params.extend([user_id, user_id])
        cur.execute(query, params)
        books_data = cur.fetchall()
        
        feedback_books = []
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            feedback_books.append(book_info)
        
        return feedback_books
    except Exception as e:
        print(f"Error getting feedback-based books: {e}")
        return []

def get_default_recommendations(cur, preferred_author, preferred_genre):
    """Get default recommended books based on user preferences"""
    try:
        # Get books with similar genres or authors
        if preferred_author and preferred_genre:
            query = """
                SELECT book_id, title, author, genre, ISBN 
                FROM new_book_table 
                WHERE (LOWER(author) LIKE LOWER(%s) OR LOWER(genre) LIKE LOWER(%s))
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
        
        # Convert to list of dictionaries and add consistent ratings
        recommended_books = []
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            recommended_books.append(book_info)
        
        return recommended_books
    except Exception as e:
        print(f"Error getting default recommendations: {e}")
        return []


def get_content_based_books(cur, user_id):
    """Get books similar to those the user has favorited or highly rated"""
    try:
        # Get user's favorite books or highly rated books
        cur.execute("""
            SELECT DISTINCT b.genre, b.author
            FROM new_book_table b
            JOIN (
                SELECT book_id FROM favorite_book_table WHERE user_id = %s
                UNION
                SELECT book_id FROM rating_table WHERE user_id = %s AND rating >= 4
            ) user_books ON b.book_id = user_books.book_id
        """, (user_id, user_id))
        
        user_preferences = cur.fetchall()
        
        if not user_preferences:
            # If no favorites or highly rated books, get recently rated books
            cur.execute("""
                SELECT DISTINCT b.genre, b.author
                FROM new_book_table b
                JOIN rating_table r ON b.book_id = r.book_id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
                LIMIT 5
            """, (user_id,))
            user_preferences = cur.fetchall()
        
        if not user_preferences:
            return []
        
        # Build query for books with similar genres or authors
        genre_conditions = []
        author_conditions = []
        params = []
        
        for pref in user_preferences:
            genre_conditions.append("LOWER(genre) LIKE LOWER(%s)")
            author_conditions.append("LOWER(author) LIKE LOWER(%s)")
            params.extend([f"%{pref[0]}%", f"%{pref[1]}%"])
        
        genre_query = " OR ".join(genre_conditions)
        author_query = " OR ".join(author_conditions)
        
        # Get books with similar genres or authors that user hasn't read
        query = f"""
            SELECT DISTINCT book_id, title, author, genre, ISBN
            FROM new_book_table
            WHERE ({genre_query} OR {author_query})
            AND book_id NOT IN (
                SELECT book_id FROM rating_table WHERE user_id = %s
                UNION
                SELECT book_id FROM favorite_book_table WHERE user_id = %s
            )
            ORDER BY RAND()
            LIMIT 10
        """
        
        params.extend([user_id, user_id])
        cur.execute(query, params)
        books_data = cur.fetchall()
        
        content_books = []
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            content_books.append(book_info)
        
        return content_books
    except Exception as e:
        print(f"Error getting content-based books: {e}")
        return []

def get_feedback_based_books(cur, user_id):
    """Get books based on user's feedback keywords"""
    try:
        # Get keywords from user's feedback
        cur.execute("""
            SELECT feedback FROM feedback_table WHERE user_id = %s AND feedback IS NOT NULL
        """, (user_id,))
        
        feedbacks = cur.fetchall()
        
        if not feedbacks:
            return []
        
        # Extract keywords from feedback (simple approach)
        keywords = set()
        for feedback in feedbacks:
            words = feedback[0].lower().split()
            # Filter for meaningful words (skip common words)
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'if', 'it', 'its', 'they', 'them', 'their', 'he', 'she', 'him', 'her', 'his', 'hers', 'we', 'us', 'our', 'you', 'your', 'yours', 'i', 'me', 'my', 'mine'}
            for word in words:
                # Remove punctuation
                word = ''.join(char for char in word if char.isalnum())
                if len(word) > 3 and word not in common_words:
                    keywords.add(word)
        
        if not keywords:
            return []
        
        # Build query for books with titles, authors, or genres containing these keywords
        keyword_conditions = []
        params = []
        
        for keyword in list(keywords)[:10]:  # Limit to first 10 keywords
            keyword_conditions.append("(LOWER(title) LIKE %s OR LOWER(author) LIKE %s OR LOWER(genre) LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        keyword_query = " OR ".join(keyword_conditions)
        
        # Get books matching keywords that user hasn't read
        query = f"""
            SELECT DISTINCT book_id, title, author, genre, ISBN
            FROM new_book_table
            WHERE ({keyword_query})
            AND book_id NOT IN (
                SELECT book_id FROM rating_table WHERE user_id = %s
            )
            ORDER BY RAND()
            LIMIT 10
        """
        
        params.append(user_id)
        cur.execute(query, params)
        books_data = cur.fetchall()
        
        feedback_books = []
        for book in books_data:
            # Generate consistent rating based on book properties
            rating_seed = (book[0] * 7 + len(book[1])) % 15 + 35
            rating = round(rating_seed / 10.0, 1)
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
            feedback_books.append(book_info)
        
        return feedback_books
    except Exception as e:
        print(f"Error getting feedback-based books: {e}")
        return []

def get_default_recommendations(cur, preferred_author, preferred_genre):
    """Get default recommendations based on user preferences"""
    try:
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
        
        return recommended_books_list
    except Exception as e:
        print(f"Error getting default recommendations: {e}")
        return []

# Recently Rated Books
@app.route("/recently_rated")
def recently_rated():
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get user's ratings and feedback with book details
        cur.execute("""
            SELECT r.rating_id, r.rating, r.created_at,
                   f.feedback, f.feedback_id,
                   b.book_id, b.title, b.author
            FROM rating_table r
            LEFT JOIN feedback_table f ON r.user_id = f.user_id AND r.book_id = f.book_id
            JOIN new_book_table b ON r.book_id = b.book_id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """, (session['user_id'],))
        
        ratings_data = cur.fetchall()
        cur.close()
        
        # Process the data to create a list of rated books
        rated_books = []
        for rating in ratings_data:
            book_info = {
                'rating_id': rating[0],
                'rating': rating[1],
                'rated_at': rating[2],
                'feedback': rating[3],
                'feedback_id': rating[4],
                'book_id': rating[5],
                'book_title': rating[6],
                'book_author': rating[7]
            }
            rated_books.append(book_info)
        
        return render_template('recently_rated.html', rated_books=rated_books, username=session['username'])
        
    except Exception as e:
        flash(f"Error loading rated books: {e}", "error")
        return render_template('recently_rated.html', rated_books=[], username=session['username'])

# Reading History
@app.route("/reading_history")
def reading_history():
    print("Reading history route accessed")
    print(f"Session keys: {list(session.keys())}")
    print(f"Session data: {session}")
    if 'loggedin' not in session:
        print("User not logged in")
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    print(f"User ID: {session.get('user_id')}")
    print(f"Username: {session.get('username')}")
    print(f"Role: {session.get('role')}")
    try:
        cur = mysql.connection.cursor()
        
        # Get completed books with ratings and feedback for this user
        # A book is considered "completed" if it exists in both rating_table and feedback_table
        print("Executing query...")
        cur.execute("""
            SELECT DISTINCT 
                b.book_id, 
                b.title, 
                b.author, 
                b.genre,
                r.rating,
                f.feedback,
                COALESCE(r.created_at, f.created_at) as finished_date
            FROM new_book_table b
            JOIN rating_table r ON b.book_id = r.book_id AND r.user_id = %s
            JOIN feedback_table f ON b.book_id = f.book_id AND f.user_id = %s
            ORDER BY COALESCE(r.created_at, f.created_at) DESC
        """, (session['user_id'], session['user_id']))
        
        completed_books = cur.fetchall()
        print(f"Found {len(completed_books)} completed books")
        cur.close()
        
        # Process the data to create a list of completed books
        books_list = []
        for book in completed_books:
            book_info = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'rating': book[4],
                'feedback': book[5],
                'finished_date': book[6].strftime('%Y-%m-%d %H:%M') if book[6] else 'N/A'
            }
            books_list.append(book_info)
        
        print(f"Rendering template with {len(books_list)} books")
        return render_template('reading_history.html', 
                             username=session['username'], 
                             books=books_list)
        
    except Exception as e:
        print(f"Error in reading history route: {e}")
        import traceback
        traceback.print_exc()
        flash(f"Error loading reading history: {e}", "error")
        return redirect(url_for('user_home'))

# Remove from Reading History
@app.route("/remove_from_history/<int:book_id>", methods=["POST"])
def remove_from_history(book_id):
    if 'loggedin' not in session:
        return {'success': False, 'message': 'Please log in'}, 401
    
    try:
        cur = mysql.connection.cursor()
        
        # Remove rating for this book (ensure it belongs to the current user)
        cur.execute(
            "DELETE FROM rating_table WHERE book_id = %s AND user_id = %s",
            (book_id, session['user_id'])
        )
        
        # Remove feedback for this book (ensure it belongs to the current user)
        cur.execute(
            "DELETE FROM feedback_table WHERE book_id = %s AND user_id = %s",
            (book_id, session['user_id'])
        )
        
        mysql.connection.commit()
        cur.close()
        
        return {'success': True, 'message': 'Book removed from reading history'}
        
    except Exception as e:
        return {'success': False, 'message': f'Error: {e}'}, 500

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

# Remove from Continue Reading
@app.route("/remove_from_continue_reading/<int:progress_id>", methods=["POST"])
def remove_from_continue_reading(progress_id):
    if 'loggedin' not in session:
        return {'success': False, 'message': 'Please log in'}, 401
    
    try:
        cur = mysql.connection.cursor()
        
        # Remove reading progress (ensure it belongs to the current user)
        cur.execute(
            "DELETE FROM reading_progress_table WHERE progress_id = %s AND user_id = %s",
            (progress_id, session['user_id'])
        )
        mysql.connection.commit()
        
        if cur.rowcount > 0:
            cur.close()
            return {'success': True, 'message': 'Book removed from continue reading'}
        else:
            cur.close()
            return {'success': False, 'message': 'Reading progress not found'}, 404
            
    except Exception as e:
        return {'success': False, 'message': f'Error: {e}'}, 500

# Continue Reading
@app.route("/continue_reading")
def continue_reading():
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get books with reading progress for this user
        cur.execute("""
            SELECT r.progress_id, b.book_id, b.title, b.author, b.genre, b.ISBN, b.content,
                   r.page_number, r.paused_word, r.paused_sentence,
                   r.updated_at
            FROM reading_progress_table r
            JOIN new_book_table b ON r.book_id = b.book_id
            WHERE r.user_id = %s
            ORDER BY r.updated_at DESC
        """, (session['user_id'],))
        
        books_with_progress = cur.fetchall()
        cur.close()
        
        # Process the data to create a list of books with progress
        books_list = []
        for book in books_with_progress:
            # Calculate progress percentage (assuming 100 pages per book for demo)
            # In a real implementation, you would calculate based on actual content
            progress_percentage = min(100, max(0, (book[7] or 1) / 100 * 100))  # page_number / 100 * 100
            
            book_info = {
                'progress_id': book[0],  # Added progress_id for removal
                'id': book[1],
                'title': book[2],
                'author': book[3],
                'genre': book[4],
                'isbn': book[5],
                'content': book[6] if book[6] else '',
                'page_number': book[7] or 1,
                'paused_word': book[8] or '',
                'paused_sentence': book[9] or '',
                'updated_at': book[10],
                'progress_percentage': int(progress_percentage)
            }
            books_list.append(book_info)
        
        return render_template('continue_reading.html', 
                             username=session['username'], 
                             books=books_list)
        
    except Exception as e:
        flash(f"Error loading reading progress: {e}", "error")
        return redirect(url_for('user_home'))

# Book Details
@app.route("/book/<int:book_id>")
def book_details(book_id):
    if 'loggedin' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # Updated to include content column
        cur.execute(
            "SELECT book_id, title, author, genre, ISBN, content FROM new_book_table WHERE book_id = %s",
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
                'The Catcher in the Rye': 'J.D. Salinger\'s coming-of-age novel follows teenager Holden Caulfield as he wanders New York City. A frank exploration of adolescent alienation, identity, and the loss of innocence.'
            }
            
            # Get description for the specific book title, or generate a generic one
            generic_description = (f'A compelling {book_data[3].lower()} work by {book_data[2]}. '
                                  f'This engaging book offers readers a rich literary experience that '
                                  f'explores profound themes and memorable characters, showcasing '
                                  f"the author's unique voice and storytelling mastery.")
            description = title_descriptions.get(book_data[1], generic_description)
            
            book_info = {
                'id': book_data[0],
                'title': book_data[1],
                'author': book_data[2],
                'genre': book_data[3],
                'isbn': book_data[4],
                'content': book_data[5] if book_data[5] else '',  # Use empty string if no content
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
        # Updated to include content column
        cur.execute(
            "SELECT book_id, title, author, genre, ISBN, content FROM new_book_table WHERE book_id = %s",
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
                'content': book_data[5] if book_data[5] else '',  # Use empty string if no content
                'rating': rating,
                'stars': stars
            }
            
            return render_template('read.html', book=book_info)
        else:
            flash(f"Book with ID {book_id} not found.", "error")
            return redirect(url_for('recommended_books'))
            
    except Exception as e:
        flash(f"Error loading book: {str(e)}", "error")
        return redirect(url_for('recommended_books'))

# Get Reading Progress
@app.route("/get_reading_progress/<book_id>")
def get_reading_progress(book_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to get progress.'}), 401
    
    try:
        user_id = session['user_id']
        new_book_id = book_id
        
        cur = mysql.connection.cursor()
        
        # For reading progress, we use new_book_id directly since reading_progress_table references new_book_table
        book_id = new_book_id
        
        # Get reading progress for this user and book
        cur.execute(
            """SELECT page_number, paused_word, paused_sentence 
               FROM reading_progress_table 
               WHERE user_id = %s AND book_id = %s""",
            (user_id, book_id)
        )
        progress_record = cur.fetchone()
        
        cur.close()
        
        if progress_record:
            return jsonify({
                'success': True,
                'progress': {
                    'page_number': progress_record[0],
                    'paused_word': progress_record[1],
                    'paused_sentence': progress_record[2]
                }
            })
        else:
            return jsonify({'success': True, 'progress': None})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting progress: {str(e)}'}), 500

# Save Reading Progress
@app.route("/save_reading_progress", methods=["POST"])
def save_reading_progress():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to save progress.'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']  # Use the actual session user_id
        new_book_id = data.get('book_id')  # This is from new_book_table
        page_number = data.get('page_number', 1)
        paused_word = data.get('paused_word', '')
        paused_sentence = data.get('paused_sentence', '')
        
        cur = mysql.connection.cursor()
        
        # For reading progress, we use new_book_id directly since reading_progress_table references new_book_table
        book_id = new_book_id
        
        # Check if there's already a progress record for this user and book
        cur.execute(
            "SELECT progress_id FROM reading_progress_table WHERE user_id = %s AND book_id = %s",
            (user_id, book_id)
        )
        existing_record = cur.fetchone()
        
        if existing_record:
            # Update existing record
            cur.execute(
                """UPDATE reading_progress_table 
                   SET page_number = %s, paused_word = %s, paused_sentence = %s, updated_at = CURRENT_TIMESTAMP 
                   WHERE user_id = %s AND book_id = %s""",
                (page_number, paused_word, paused_sentence, user_id, book_id)
            )
        else:
            # Insert new record
            cur.execute(
                """INSERT INTO reading_progress_table 
                   (user_id, book_id, page_number, paused_word, paused_sentence) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, book_id, page_number, paused_word, paused_sentence)
            )
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Your reading progress has been saved.'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving progress: {str(e)}'}), 500

# Save Rating and Feedback
@app.route("/save_rating_and_feedback", methods=["POST"])
def save_rating_and_feedback():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in to rate and provide feedback.'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']  # Use the actual session user_id
        new_book_id = data.get('book_id')  # This is from new_book_table
        rating = data.get('rating')
        feedback = data.get('feedback')
        
        if not all([new_book_id, rating, feedback]):
            return jsonify({'success': False, 'message': 'Missing required data.'}), 400
        
        cur = mysql.connection.cursor()
        
        # Use new_book_id directly since both rating_table and feedback_table reference new_book_table
        book_id = new_book_id
        
        # Save rating
        # Check if user has already rated this book
        cur.execute(
            "SELECT rating_id FROM rating_table WHERE user_id = %s AND book_id = %s",
            (user_id, book_id)
        )
        existing_rating = cur.fetchone()
        
        if existing_rating:
            # Update existing rating
            cur.execute(
                "UPDATE rating_table SET rating = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s AND book_id = %s",
                (rating, user_id, book_id)
            )
        else:
            # Insert new rating
            cur.execute(
                "INSERT INTO rating_table (user_id, book_id, rating) VALUES (%s, %s, %s)",
                (user_id, book_id, rating)
            )
        
        # Save feedback
        cur.execute(
            "INSERT INTO feedback_table (user_id, book_id, feedback) VALUES (%s, %s, %s)",
            (user_id, book_id, feedback)
        )
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Your rating and feedback have been saved.'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error submitting rating and feedback: {str(e)}'}), 500

# Route to create missing tables (for development purposes)
@app.route("/create_tables")
def create_tables():
    try:
        cur = mysql.connection.cursor()
        
        # Create new_book_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS new_book_table (
                book_id INT(11) NOT NULL AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                ISBN VARCHAR(20) NOT NULL,
                content LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (book_id),
                UNIQUE KEY unique_isbn (ISBN),
                INDEX idx_title (title),
                INDEX idx_author (author),
                INDEX idx_genre (genre)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create rating_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rating_table (
                rating_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                rating INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            )
        """)
        
        # Create feedback_table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback_table (
                feedback_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                feedback TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            )
        """)
        
        mysql.connection.commit()
        cur.close()
        
        return "Tables created successfully!"
        
    except Exception as e:
        return f"Error creating tables: {str(e)}"

# Route to verify database setup (for development purposes)
@app.route("/verify_db")
def verify_db():
    try:
        cur = mysql.connection.cursor()
        
        # Check if required tables exist
        tables_to_check = ['user_table', 'new_book_table', 'reading_progress_table', 'rating_table', 'feedback_table']
        existing_tables = []
        
        cur.execute("SHOW TABLES")
        all_tables = cur.fetchall()
        table_names = [table[0] for table in all_tables]
        
        for table in tables_to_check:
            if table in table_names:
                existing_tables.append(table)
        
        # Check if there are users
        cur.execute("SELECT COUNT(*) FROM user_table")
        user_count = cur.fetchone()[0]
        
        # Check if there are books
        cur.execute("SELECT COUNT(*) FROM new_book_table")
        book_count = cur.fetchone()[0]
        
        cur.close()
        
        result = {
            'existing_tables': existing_tables,
            'total_tables': len(table_names),
            'user_count': user_count,
            'book_count': book_count
        }
        
        return str(result)
        
    except Exception as e:
        return f"Error verifying database: {str(e)}"

# Route to describe table structures (for development purposes)
@app.route("/describe_tables")
def describe_tables():
    try:
        cur = mysql.connection.cursor()
        
        tables = ['reading_progress_table', 'rating_table', 'feedback_table']
        result = {}
        
        for table in tables:
            try:
                cur.execute(f"DESCRIBE {table}")
                columns = cur.fetchall()
                result[table] = [{'field': col[0], 'type': col[1], 'null': col[2], 'key': col[3], 'default': col[4], 'extra': col[5]} for col in columns]
            except Exception as e:
                result[table] = f"Error describing table: {str(e)}"
        
        cur.close()
        return str(result)
        
    except Exception as e:
        return f"Error describing tables: {str(e)}"

# Route to get sample data (for development purposes)
@app.route("/sample_data")
def sample_data():
    try:
        cur = mysql.connection.cursor()
        
        # Get a sample user
        cur.execute("SELECT user_id FROM user_table LIMIT 1")
        user = cur.fetchone()
        user_id = user[0] if user else None
        
        # Get a sample book from new_book_table
        cur.execute("SELECT book_id FROM new_book_table LIMIT 1")
        book = cur.fetchone()
        new_book_id = book[0] if book else None
        
        # Check if book_table exists and get a sample book
        try:
            cur.execute("SELECT book_id FROM book_table LIMIT 1")
            book = cur.fetchone()
            old_book_id = book[0] if book else None
        except:
            old_book_id = None
        
        cur.close()
        
        return f"Sample user_id: {user_id}, Sample new_book_id: {new_book_id}, Sample book_id: {old_book_id}"
        
    except Exception as e:
        return f"Error getting sample data: {str(e)}"

# Route to verify saved data (for development purposes)
@app.route("/verify_saved_data")
def verify_saved_data():
    try:
        cur = mysql.connection.cursor()
        
        # Check reading progress
        cur.execute("SELECT * FROM reading_progress_table WHERE user_id = 66 AND book_id = 5576")
        reading_progress = cur.fetchall()
        
        # Check rating
        cur.execute("SELECT * FROM rating_table WHERE user_id = 66 AND book_id = 5576")
        rating = cur.fetchall()
        
        # Check feedback
        cur.execute("SELECT * FROM feedback_table WHERE user_id = 66 AND book_id = 5576")
        feedback = cur.fetchall()
        
        cur.close()
        
        result = {
            'reading_progress': len(reading_progress),
            'rating': len(rating),
            'feedback': len(feedback)
        }
        
        return str(result)
        
    except Exception as e:
        return f"Error verifying saved data: {str(e)}"

# Route to update database schema (for development purposes)
@app.route("/update_schema")
def update_schema():
    try:
        cur = mysql.connection.cursor()
        
        # First, drop foreign key constraints that reference book_table
        try:
            cur.execute("ALTER TABLE rating_table DROP FOREIGN KEY IF EXISTS fk_rating_book")
            print("Dropped foreign key constraint fk_rating_book")
        except Exception as e:
            print(f"Note: fk_rating_book constraint may not exist: {e}")
        
        # Drop foreign key constraints in feedback_table
        try:
            cur.execute("ALTER TABLE feedback_table DROP FOREIGN KEY IF EXISTS fk_feedback_book")
            print("Dropped foreign key constraint fk_feedback_book")
        except Exception as e:
            print(f"Note: fk_feedback_book constraint may not exist: {e}")
        
        # Now update the foreign key references to point to new_book_table
        try:
            cur.execute("""
                ALTER TABLE rating_table 
                ADD CONSTRAINT fk_rating_new_book 
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) 
                ON DELETE CASCADE
            """)
            print("Added foreign key constraint fk_rating_new_book")
        except Exception as e:
            print(f"Note: Could not add fk_rating_new_book constraint: {e}")
        
        try:
            cur.execute("""
                ALTER TABLE feedback_table 
                ADD CONSTRAINT fk_feedback_new_book 
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) 
                ON DELETE CASCADE
            """)
            print("Added foreign key constraint fk_feedback_new_book")
        except Exception as e:
            print(f"Note: Could not add fk_feedback_new_book constraint: {e}")
        
        # Drop the old book_table
        try:
            cur.execute("DROP TABLE IF EXISTS book_table")
            print("Dropped book_table successfully")
        except Exception as e:
            print(f"Note: Could not drop book_table: {e}")
        
        mysql.connection.commit()
        cur.close()
        
        return "Database schema updated successfully!"
        
    except Exception as e:
        return f"Error updating schema: {str(e)}"

# Route to fix table structures (for development purposes)
@app.route("/fix_table_structure")
def fix_table_structure():
    try:
        cur = mysql.connection.cursor()
        
        # Drop existing tables if they exist
        try:
            cur.execute("DROP TABLE IF EXISTS feedback_table")
            print("Dropped feedback_table")
        except Exception as e:
            print(f"Note: Could not drop feedback_table: {e}")
            
        try:
            cur.execute("DROP TABLE IF EXISTS rating_table")
            print("Dropped rating_table")
        except Exception as e:
            print(f"Note: Could not drop rating_table: {e}")
        
        # Create rating_table with correct structure
        cur.execute("""
            CREATE TABLE rating_table (
                rating_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                rating INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            )
        """)
        print("Created rating_table with correct structure")
        
        # Create feedback_table with correct structure
        cur.execute("""
            CREATE TABLE feedback_table (
                feedback_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                feedback TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES new_book_table(book_id) ON DELETE CASCADE
            )
        """)
        print("Created feedback_table with correct structure")
        
        mysql.connection.commit()
        cur.close()
        
        return "Table structures fixed successfully!"
        
    except Exception as e:
        return f"Error fixing table structures: {str(e)}"

# Route to test database operations (for development purposes)
@app.route("/test_db_ops")
def test_db_ops():
    try:
        cur = mysql.connection.cursor()
        
        # Test inserting into reading_progress_table
        try:
            cur.execute("""
                INSERT INTO reading_progress_table 
                (user_id, book_id, page_number, paused_word, paused_sentence) 
                VALUES (%s, %s, %s, %s, %s)
            """, (1, 1, 5, "test", "This is a test sentence"))
            mysql.connection.commit()
            reading_result = "✓ Successfully inserted into reading_progress_table"
        except Exception as e:
            reading_result = f"✗ Error inserting into reading_progress_table: {str(e)}"
        
        # Test inserting into rating_table
        try:
            cur.execute("""
                INSERT INTO rating_table 
                (user_id, book_id, rating) 
                VALUES (%s, %s, %s)
            """, (1, 1, 4))
            mysql.connection.commit()
            rating_result = "✓ Successfully inserted into rating_table"
        except Exception as e:
            rating_result = f"✗ Error inserting into rating_table: {str(e)}"
        
        # Test inserting into feedback_table
        try:
            cur.execute("""
                INSERT INTO feedback_table 
                (user_id, book_id, feedback) 
                VALUES (%s, %s, %s)
            """, (1, 1, "This is a test feedback"))
            mysql.connection.commit()
            feedback_result = "✓ Successfully inserted into feedback_table"
        except Exception as e:
            feedback_result = f"✗ Error inserting into feedback_table: {str(e)}"
        
        # Clean up test data
        try:
            cur.execute("DELETE FROM reading_progress_table WHERE user_id = 1 AND book_id = 1")
            cur.execute("DELETE FROM rating_table WHERE user_id = 1 AND book_id = 1")
            cur.execute("DELETE FROM feedback_table WHERE user_id = 1 AND book_id = 1")
            mysql.connection.commit()
            cleanup_result = "✓ Test data cleaned up successfully"
        except Exception as e:
            cleanup_result = f"✗ Error cleaning up test data: {str(e)}"
        
        cur.close()
        
        return f"""
        Database Operations Test Results:
        {reading_result}
        {rating_result}
        {feedback_result}
        {cleanup_result}
        """
        
    except Exception as e:
        return f"Error testing database operations: {str(e)}"

# View Ratings (Admin only)
@app.route("/view_ratings")
def view_ratings():
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get all ratings with user and book information, including user email
        cur.execute("""
            SELECT r.rating_id, r.rating, r.created_at,
                   u.username, u.user_id, u.email,
                   b.title, b.book_id
            FROM rating_table r
            JOIN user_table u ON r.user_id = u.user_id
            JOIN new_book_table b ON r.book_id = b.book_id
            ORDER BY r.created_at DESC
        """)
        ratings_data = cur.fetchall()
        
        # Get number of users who rated each book
        cur.execute("""
            SELECT b.title, b.book_id, COUNT(DISTINCT r.user_id) as user_count
            FROM new_book_table b
            LEFT JOIN rating_table r ON b.book_id = r.book_id
            GROUP BY b.book_id, b.title
            ORDER BY user_count DESC
        """)
        book_user_counts = cur.fetchall()
        
        # Get rating distribution for each book (1-5 stars)
        cur.execute("""
            SELECT b.title, b.book_id,
                   SUM(CASE WHEN r.rating = 1 THEN 1 ELSE 0 END) as rating_1,
                   SUM(CASE WHEN r.rating = 2 THEN 1 ELSE 0 END) as rating_2,
                   SUM(CASE WHEN r.rating = 3 THEN 1 ELSE 0 END) as rating_3,
                   SUM(CASE WHEN r.rating = 4 THEN 1 ELSE 0 END) as rating_4,
                   SUM(CASE WHEN r.rating = 5 THEN 1 ELSE 0 END) as rating_5
            FROM new_book_table b
            LEFT JOIN rating_table r ON b.book_id = r.book_id
            GROUP BY b.book_id, b.title
            ORDER BY b.title
        """)
        rating_distributions = cur.fetchall()
        
        # Get all books from new_book_table for search suggestions
        cur.execute("""
            SELECT book_id, title, ISBN
            FROM new_book_table
            ORDER BY title
        """)
        all_books = cur.fetchall()
        
        cur.close()
        
        ratings_list = []
        for rating in ratings_data:
            rating_info = {
                'id': rating[0],
                'rating': rating[1],
                'created_at': rating[2],
                'username': rating[3],
                'user_id': rating[4],
                'email': rating[5],
                'book_title': rating[6],
                'book_id': rating[7]
            }
            ratings_list.append(rating_info)
        
        # Process book user counts
        book_stats = []
        for book in book_user_counts:
            book_stats.append({
                'title': book[0],
                'book_id': book[1],
                'user_count': book[2]
            })
        
        # Process rating distributions
        rating_stats = []
        for book in rating_distributions:
            rating_stats.append({
                'title': book[0],
                'book_id': book[1],
                'rating_1': book[2] or 0,
                'rating_2': book[3] or 0,
                'rating_3': book[4] or 0,
                'rating_4': book[5] or 0,
                'rating_5': book[6] or 0
            })
        
        # Process all books for search suggestions
        all_books_list = []
        for book in all_books:
            all_books_list.append({
                'book_id': book[0],
                'title': book[1],
                'isbn': book[2] or ''
            })
        
        return render_template('view_ratings.html', 
                             ratings=ratings_list, 
                             book_stats=book_stats, 
                             rating_stats=rating_stats,
                             all_books=all_books_list)
        
    except Exception as e:
        flash(f"Error loading ratings: {e}", "error")
        return redirect(url_for('admin_home'))

# View Feedback (Admin only)
@app.route("/view_feedback")
def view_feedback():
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get all feedback with user and book information, including user email
        cur.execute("""
            SELECT f.feedback_id, f.feedback, f.created_at,
                   u.username, u.user_id, u.email,
                   b.title, b.book_id, b.author
            FROM feedback_table f
            JOIN user_table u ON f.user_id = u.user_id
            JOIN new_book_table b ON f.book_id = b.book_id
            ORDER BY f.feedback_id ASC
        """)
        feedback_data = cur.fetchall()
        
        # Get all books from new_book_table for search suggestions
        cur.execute("""
            SELECT book_id, title, ISBN, author
            FROM new_book_table
            ORDER BY title
        """)
        all_books = cur.fetchall()
        
        cur.close()
        
        feedback_list = []
        for feedback in feedback_data:
            feedback_info = {
                'id': feedback[0],
                'feedback': feedback[1],
                'created_at': feedback[2],
                'username': feedback[3],
                'user_id': feedback[4],
                'email': feedback[5],
                'book_title': feedback[6],
                'book_id': feedback[7],
                'book_author': feedback[8]  # Added book author
            }
            feedback_list.append(feedback_info)
        
        # Process all books for search suggestions
        all_books_list = []
        for book in all_books:
            all_books_list.append({
                'book_id': book[0],
                'title': book[1],
                'isbn': book[2] or '',
                'author': book[3] or ''
            })
        
        return render_template('view_feedback.html', feedbacks=feedback_list, all_books=all_books_list)
        
    except Exception as e:
        flash(f"Error loading feedback: {e}", "error")
        return redirect(url_for('admin_home'))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
