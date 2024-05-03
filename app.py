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
    return render_template('placeholder.html')

# Route for handling user login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # Get username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the database and fetch user data
        con = get_db_connection()
        cur = con.cursor() # enable to execute SQL query on the database
        # select all columns where the `name` matches the provided `username`
        cur.execute("SELECT * FROM user WHERE name = ?", (username,))
        # fetch the first row
        user = cur.fetchone()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user[3], password): # needs to using integer indices to avoid TypeError bug
            session["username"] = user[1]  
            session["email"] = user[2]

            # Record the login time
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("INSERT INTO login_history (username, login_time) VALUES (?, ?)", (username, login_time))
            con.commit()   

            # redirects the user to the 'user' endpoint
            return redirect(url_for("user"))
        # Flash a message for incorrect username or password
        else:
            flash("Username and Password Mismatch", "danger")
    
    # Render the login page
    return render_template('login.html')

# Route for the user's homepage
@app.route('/user')
def user():
    # Check if the user is logged in
    if 'username' in session:
        # Render the user's homepage
        return render_template("homepage.html")
    else:
        # Redirect to the login page if not logged in
        return redirect(url_for("login"))

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get user input from the registration form
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # Validate email format
            if not is_valid_email(email):
                flash("Invalid email format", "danger")
                return redirect(url_for('register'))
            
            # Connect to the database and check if the username already exists
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE name = ?", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                # Flash an error message if the username already exists
                flash('Username already exists.', 'danger')
                return redirect(url_for('register'))

            # Hash the password before storing it in the database
            hashed_password = generate_password_hash(password)
            # Insert the new user data into the database
            cur.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            con.commit()  # Commit the changes to the database
            # flash an message prompts user registration successfully 
            flash("User Added Successfully", "success")
            return redirect(url_for("index"))

        except Exception as e:
            # Flash an error message if an exception occurs during registration
            flash("Error in Insert Operation: " + str(e), "danger")

        finally:
            # Close the database connection
            con.close()

    # Render the registration form
    return render_template('register.html')

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
