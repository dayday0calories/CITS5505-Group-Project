from app import db
from datetime import datetime
from flask_login import UserMixin

# Define the User model
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    

# Define the LoginHistory model    
class LoginHistory(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String[64], index = True)
    login_time = db.Column(db.DateTime)
    logout_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<LoginHistory {}>'.format(self.id)



# Define the post model
class Post(db.Model):
    # Represents a post in the forum
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the post
    title = db.Column(db.String(255), nullable=False)  # Title of the post, cannot be empty
    category = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)  # Content of the post, cannot be empty
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Record of when the post was created, defaults to current time
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    # Track views and replies
    views = db.Column(db.Integer, default=0)
    replies_count = db.Column(db.Integer, default=0)

    # Date of last reply
    last_reply_date = db.Column(db.DateTime,default=datetime.utcnow)


    # Relationship to Reply model, a post can have many replies
    replies = db.relationship('Reply', backref='post', lazy='dynamic')


# Defien the reply model
class Reply(db.Model):
    # Represents a reply to a post
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the reply
    content = db.Column(db.Text, nullable=False)  # Content of the reply, cannot be empty
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # Foreign key to the post that this reply is associated with
    parent_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=True)  # Enables hierarchical structure for replies
    # Relationship for hierarchical replies; replies can have children and a parent
    children = db.relationship('Reply', backref=db.backref('parent', remote_side=[id]), lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Record of when the reply was created, defaults to current UTC time
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('replies', lazy=True))





