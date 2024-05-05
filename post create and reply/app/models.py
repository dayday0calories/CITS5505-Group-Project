from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy with Flask
db = SQLAlchemy()

class Post(db.Model):
    # Represents a post in the forum
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the post
    title = db.Column(db.String(255), nullable=False)  # Title of the post, cannot be empty
    content = db.Column(db.Text, nullable=False)  # Content of the post, cannot be empty
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Record of when the post was created, defaults to current time
    # Relationship to Tag model, many-to-many, lazy loading with 'subquery' for better performance on read operations
    tags = db.relationship('Tag', secondary='post_tags', lazy='subquery')
    # Relationship to Reply model, a post can have many replies
    replies = db.relationship('Reply', backref='post', lazy=True)

class Reply(db.Model):
    # Represents a reply to a post
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the reply
    content = db.Column(db.Text, nullable=False)  # Content of the reply, cannot be empty
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # Foreign key to the post that this reply is associated with
    parent_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=True)  # Enables hierarchical structure for replies
    # Relationship for hierarchical replies; replies can have children and a parent
    children = db.relationship('Reply', backref=db.backref('parent', remote_side=[id]), lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Record of when the reply was created, defaults to current UTC time

class Tag(db.Model):
    # Represents a tag that can be associated with a post
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the tag
    name = db.Column(db.String(100), unique=True)  # Name of the tag, must be unique
    # Relationship to Post model, many-to-many, lazy loading with 'subquery' for better performance on read operations
    posts = db.relationship('Post', secondary='post_tags', lazy='subquery')

# Association table for the many-to-many relationship between posts and tags
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),  # Link to the Post model
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)  # Link to the Tag model
)


