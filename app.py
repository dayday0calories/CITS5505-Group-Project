from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import re
from datetime import datetime
from app.models.models import db,User, LoginHistory, Post, Reply
from flask_sqlalchemy import SQLAlchemy
from config import Config 
from flask_login import LoginManager
from flask_login import current_user, login_required, login_user
from app.forms import PostForm

# Generate a secret key for the session
secret_key = secrets.token_hex(24) 

# Create a Flask application instance
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = secret_key

# Link SQLAlchemy to the app
db.init_app(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'  # Specify the route where the login view is accessible

# Get the curret user id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

# Route for the post page
@app.route('/posts')
def view_post():
    posts = Post.query.all() # Fetch posts data from the database
    for post in posts:
        last_reply = Reply.query.filter_by(post_id=post.id).order_by(Reply.created_at.desc()).first()
        if last_reply:  # Check if there is a reply
            post.last_replier_username = last_reply.user.username
            post.last_reply_date = last_reply.created_at
        else:
            post.last_replier_username = 'No replies yet'
            post.last_reply_date = None  # 
    return render_template('posts.html', posts = posts)

# Route for the main page
@app.route('/forums')
def forums():
    return render_template('forums.html')

# Route for detail page
@app.route('/detail')
def detail():
    return render_template('detail.html')

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
                
                # Change the status as login
                login_user(user)
                flash("Logged in successfully.", "success")

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


# Create post
@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('You must be logged in to view this page.')
        return redirect(url_for('register'))  
        # Redirect them to the registration page

    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, category=form.category.data, content=form.content.data, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('view_post'))  # Redirect to posts page
    return render_template('create-post.html', form=form)


# handle the pics
@app.route('/upload/', methods=['POST'])
def upload():
    file = request.files['upload']
    filename = secure_filename(file.filename)
    filepath = os.path.join('path/to/save', filename)
    file.save(filepath)
    return jsonify({
        'uploaded': 1,
        'fileName': filename,
        'url': url_for('static', filename='path/to/save/' + filename)
    })

@app.route('/detail/<int:post_id>')
def details(post_id):
    post = Post.query.get_or_404(post_id)  # Fetch the post or return 404 if not found
    post.views += 1  # Increment the view count
    db.session.commit()
    return render_template('detail.html', post=post)


# Handle submit reply
@app.route('/submit-reply/<int:post_id>', methods=['POST'])
def submit_reply(post_id):
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('You must be logged in to view this page.')
        return redirect(url_for('register'))  
        # Redirect them to the registration page

    post = Post.query.get_or_404(post_id)  # Make sure the post exists
    reply_content = request.form['reply_content']
    if reply_content:
        reply = Reply(content=reply_content, post_id=post.id, user_id=current_user.id)
        db.session.add(reply)
        db.session.commit()
        #Increment the reply count
        post.replies_count += 1 
        db.session.commit()

        flash('Your reply has been posted.', 'success')
    else:
        flash('Reply cannot be empty.', 'error')
    return redirect(url_for('details', post_id=post_id))  # Redirect back to the post detail page





# Run the flask application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

