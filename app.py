from flask import Flask, render_template, request, flash, redirect,url_for,session
import sqlite3

app = Flask(__name__)
app.secret_key="123"

con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key, name text, address text, contact integer, mail text)")
con.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from customer where name="?" and mail="?",(name,password))
        data = cur.fetchone

        if data:
            session["username"] = data["username"]
            session["email"] = data["email"]
            return redirect("customer")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))

@app.route('/customer',methods = ["GET",["POST"]])
def customer():
    return render_template("customer.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['sername']
            email = request.form['email']
            password = request.form['password']
        
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('register.html', message='Username already exists.')
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into customer(username,email,password)values(?,?,?)",())
            con.commit()
            flash("Record Added Successfully","success")
        except:
            flash("Error in Insert Operation", "danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

if__name__ = '__main__':
    app.run(debug=True)
