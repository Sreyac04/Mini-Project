from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__)

# (No routes needed here for now. You can add authentication-related routes later.)
def login():
    return render_template('login.html')

