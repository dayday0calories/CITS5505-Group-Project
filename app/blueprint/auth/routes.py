from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required, logout_user
from . import auth
from app.models.models import User, db, LoginHistory
from datetime import datetime
import re


# Function to verify email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@auth.route('/')
def index():
    return render_template('posts/view_posts.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            # Record the login time
            login_time = datetime.now()
            login_history = LoginHistory(username=username, login_time=login_time)
            db.session.add(login_history)
            db.session.commit()
            return redirect(url_for("pr.view_post"))  # Adjust the redirect as needed
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not is_valid_email(email):
            flash("Invalid email format", "warning")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template('auth/register.html')




# Route for user logout
@auth.route('/logout')
@login_required
def logout():
    """Logout user and record logout time."""

    if 'username' in session:
        # Get the current user's username
        username = session['username']

        # Query for the most recent login entry for the user
        login_history = LoginHistory.query.filter_by(username=username, logout_time=None).order_by(LoginHistory.id.desc()).first()

        if login_history:
            # Update the logout time for the most recent login entry
            login_history.logout_time = datetime.now()
            db.session.commit()

     # logout the user
    logout_user()
    
    # Redirect to the home page
    return redirect(url_for("auth.index"))






