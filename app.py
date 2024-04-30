from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

secret_key = secrets.token_hex(24)

app = Flask(__name__)
app.secret_key = secret_key

def get_db_connection():
    return sqlite3.connect("database.db")

@app.route('/')
def index():
    return render_template('placeholder.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE name = ?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user['password'], password):
            session["username"] = user['name']  
            session["email"] = user['email']     

            return redirect(url_for("user"))
        else:
            flash("Username and Password Mismatch", "danger")
    
    return render_template('login.html')

@app.route('/user')
def user():
    if 'username' in session:
        return render_template("homepage.html")
    else:
        return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE name = ?", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                flash('Username already exists.', 'danger')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)
            cur.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            con.commit()  # Commit the changes to the database
            flash("Record Added Successfully", "success")
            return redirect(url_for("index"))

        except Exception as e:
            flash("Error in Insert Operation: " + str(e), "danger")

        finally:
            con.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
