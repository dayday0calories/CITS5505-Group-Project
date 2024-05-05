from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import re
from datetime import datetime
from app.models.models import db,User, LoginHistory
from flask_sqlalchemy import SQLAlchemy
from config import Config 

# Generate a secret key for the session
secret_key = secrets.token_hex(24) 

# Create a Flask application instance
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = secret_key

# Link SQLAlchemy to the app
db.init_app(app)

# Function to verify email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Route for the home page
@app.route('/')
def index():
    return render_template('forums.html')

# Route for the register page
@app.route('/register')
def register():
    return render_template('register.html')

# Route for handling user login and registration
@app.route('/auth', methods=["POST"])
def auth():
    """Authenticate user login or register a new user."""
    if request.method == 'POST':
        # Get username, password, and email from the form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if user exists
        user = User.query.filter_by(username = username).first()

        # If user exists, it's a login attempt
        if user:
            if not is_valid_email(email):
                flash("Invalid email format", "warning") # flash message for invalid email format
                return redirect(url_for("register"))
            
            if check_password_hash(user.password_hash, password) and user.email == email: # Check if the password is correct
                session["username"] = user.username 
                session["email"] = user.email

                # Record the login time
                login_time = datetime.now()
                login_history = LoginHistory(username = username, login_time = login_time)
                db.session.add(login_history)
                db.session.commit()
                
                # Redirect the user to the forum page
                return redirect(url_for("index"))
            else:
                flash("Username and Password or Email Mismatch", "danger")
                # wrong password or email, redirect to register page
                return redirect(url_for("register"))
        # If user doesn't exist, it's a registration attempt
        else:
            # Validate email format
            if not is_valid_email(email):
                flash("Invalid email format", "warning")
                return redirect(url_for("register"))
            
            # Hash the password before storing it in the database
            hashed_password = generate_password_hash(password)
            # Insert the new user data into the database
            new_user = User(username = username, email=email,password_hash = hashed_password)
            db.session.add(new_user)
            db.session.commit() # Commit the change to the database
            flash("User Added Successfully", "success")
            session["username"] = username
            session["email"] = email
            return redirect(url_for("index"))

    # Render the home page
    return redirect(url_for("index"))

# Route for user logout
@app.route('/logout')
def logout():
    """Logout user and record logout time."""
    if 'username' in session:
        # Get the current user's username
        username = session['username']

        # Update the logout time for the user
        login_history = LoginHistory.query.filter_by(username, logout_time=None).first
        if login_history:
            login_history.logout_time = datetime.now()
            db.session.commit()
    
    # Clear the session data
    session.clear()
    # Redirect to the home page
    return redirect(url_for("index"))

# Run the flask application
if __name__ == '__main__':
    app.run(debug=True)
