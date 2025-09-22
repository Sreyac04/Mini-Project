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
            
    # MODIFIED: Updated file paths to look inside the /data folder
    authors_list = read_csv('data/authors.csv')
    genres_list = read_csv('data/genre.csv')
    
    return render_template("preference.html", authors=authors_list, genres=genres_list)

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
            
            # Get authors and genres lists for dropdowns
            authors_list = read_csv('data/authors.csv')
            genres_list = read_csv('data/genre.csv')
            
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

if __name__ == "__main__":
    app.run(debug=True)