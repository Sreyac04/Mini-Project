from flask import Flask, render_template, request, redirect, url_for, flash

def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key"  # Replace with a secure key in production

    @app.route("/")
    def landing():
        return render_template("landing.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if username and password:
                flash(f"Welcome back, {username}!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Please enter both a username and a password.", "danger")
                return redirect(url_for("login"))
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        return "<h1>Welcome to your Dashboard!</h1><p>You have successfully logged in.</p>"

    return app
