from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder="app/templates")
app.secret_key = "your_secret_key_here_please_change_this"  # 🔑 Important: Change this to a random, complex string for security

# ⚙️ MySQL database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_engine' # Ensure this matches your database name

mysql = MySQL(app)

@app.route("/")
def landing():
    # If a user is logged in, redirect them based on their role
    if 'loggedin' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_home'))
        else: # Default to user_home if not admin
            return redirect(url_for('user_home'))
    # If not logged in, show the landing page or redirect to login
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        cur = mysql.connection.cursor()
        # ⚠️ Security Note: In a production environment, never store or compare passwords as plaintext.
        # Always use strong hashing and salting (e.g., bcrypt) for passwords.
        cur.execute("SELECT user_id, username, role FROM user_table WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone() # Fetches one row, which is a tuple
        cur.close()

        if user:
            # User found, set session variables
            session['loggedin'] = True
            session['user_id'] = user[0]    # user_id is the first element
            session['username'] = user[1]   # username is the second element
            session['role'] = user[2]       # role is the third element (index 2)
            
            flash(f"Welcome, {session['username']}!", "success")
            if session['role'] == 'admin':
                return redirect(url_for("admin_home"))
            else:
                return redirect(url_for("user_home"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    # Remove session variables
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route("/user_home")
def user_home():
    # Ensure user is logged in and has the 'user' role
    if 'loggedin' in session and session['role'] == 'user':
        return render_template("user.html", username=session['username'])
    flash("Please log in to access this page.", "error")
    return redirect(url_for('login'))

@app.route("/admin_home")
def admin_home():
    # Ensure user is logged in and has the 'admin' role
    if 'loggedin' in session and session['role'] == 'admin':
        return render_template("admin.html", username=session['username'])
    flash("Access denied. Admins only!", "error")
    return redirect(url_for('login'))
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user_table (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        mysql.connection.commit()
        cur.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
