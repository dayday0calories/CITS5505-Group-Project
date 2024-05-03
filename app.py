from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import re
from datetime import datetime

# Generate a secret key for the session
secret_key = secrets.token_hex(24) 

# Create a Flask application instance
app = Flask(__name__)
app.secret_key = secret_key

# Connect to the sqlite3 database
def get_db_connection():
    return sqlite3.connect("database.db")

# Function to verify email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Route for the home page
@app.route('/')
def index():
    return render_template('forums.html')

# Route for handling user login and registration
@app.route('/auth', methods=["POST"])
def auth():
    if request.method == 'POST':
        # Get username and password from the form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Connect to the database and check if the user exists
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE name = ?", (username,))
        user = cur.fetchone()

        # If user exists, it's a login attempt
        if user:
            if check_password_hash(user[3], password): # Check if the password is correct
                session["username"] = user[1]  
                session["email"] = user[2]

                # Record the login time
                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("INSERT INTO login_history (username, login_time) VALUES (?, ?)", (username, login_time))
                con.commit()   

                # Redirect the user to the forum page
                return redirect(url_for("forum"))
            else:
                flash("Username and Password Mismatch", "danger")
        else:
            # If user doesn't exist, it's a registration attempt
            if not is_valid_email(email):
                flash("Invalid email format", "danger")
            else:
                # Hash the password before storing it in the database
                hashed_password = generate_password_hash(password)
                # Insert the new user data into the database
                cur.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
                con.commit()  # Commit the changes to the database
                flash("User Added Successfully", "success")

    # Render the home page
    return redirect(url_for("index"))

# Route for the forum page
@app.route('/forum')
def forum():
    return render_template('forum.html')

# Route for user logout
@app.route('/logout')
def logout():
    if 'username' in session:
        # Get the current user's username
        username = session['username']

        # Connect to the database and update the logout time for the user
        con = get_db_connection()
        cur = con.cursor()
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("UPDATE login_history SET logout_time = ? WHERE username = ? AND logout_time IS NULL", (logout_time, username))
        con.commit()

    # Clear the session data
    session.clear()
    # Redirect to the home page
    return redirect(url_for("index"))

# Run the flask application
if __name__ == '__main__':
    app.run(debug=True)