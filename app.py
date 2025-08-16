from werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import re

app = Flask(__name__, template_folder="app/templates")
app.secret_key = "your_secret_key_here_please_change_this"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_engine'

mysql = MySQL(app)

# Landing Page
@app.route("/")
def landing():
    if 'loggedin' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_home'))
        else:
            return redirect(url_for('login'))
    return render_template("landing.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        # Server-side validation
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format.", "error")
            return render_template("login.html")

        if not password or len(password ) < 5:
            flash("Password must be at least 5 characters long.", "error")
            return render_template("login.html")

        # DB check
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, username, role, password FROM user_table WHERE email=%s", (email,))

        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['loggedin'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]

            flash(f"Welcome, {session['username']}!", "success")
            if session['role'] == 'admin':
                return redirect(url_for("admin_home"))
            else:
                return redirect(url_for("user_home"))
        else:
            flash("Invalid email or password.", "error")
            return render_template("login.html")

    return render_template("login.html")

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
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        dob = request.form.get("dob")
        gender = request.form.get("gender")

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """INSERT INTO user_table 
                   (username, password, email, phone_no, dob, gender, role) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (username, hashed_password, email, phone_number, dob, gender, 'user')
            )
            mysql.connection.commit()
            cur.close()

            flash("Registration complete! Please log in.", "success")
            return redirect(url_for("preferences"))

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return render_template("register.html")

    return render_template("register.html")


# Preferences Step 2
@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if request.method == "POST":

        if 'temp_user' not in session:
            flash("Session expired. Please register again.", "error")
            return redirect(url_for("register"))

        temp_user = session['temp_user']
        selected_authors = request.form.getlist("authors")
        selected_genres = request.form.getlist("genres")

        temp_user['authors'] = selected_authors
        temp_user['genres'] = selected_genres
        session['temp_user'] = temp_user

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO user_table  
               (username, password, email, phone_no, dob, gender, role) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                temp_user['username'],
                temp_user['password'],
                temp_user['email'],
                temp_user['phone_number'],
                temp_user['dob'],
                temp_user['gender'],
                'user'
            )
        )
        mysql.connection.commit()
        cur.close()

        session.pop('temp_user', None)

        flash("Registration complete! Please log in.", "success")
        return redirect(url_for("user_home"))

    temp_user = session.get('temp_user', {})
    return render_template(
        "preference.html",
        selected_authors=temp_user.get('authors', []),
        selected_genres=temp_user.get('genres', [])
    )

if __name__ == "__main__":
    app.run(debug=True)
