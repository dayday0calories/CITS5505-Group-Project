from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Post, Reply, Tag
from .forms import PostForm, ReplyForm

bp = Blueprint('forum', __name__)  # Blueprint setup for modular handling of routes

@bp.route('/')
def index():
    # Route to display all posts
    posts = Post.query.all()  # Fetch all posts from the database
    return render_template('view_post.html', posts=posts)  # Render the view with posts

@bp.route('/create', methods=['GET', 'POST'])
def create_post():
    # Route for creating a new post
    form = PostForm()
    if form.validate_on_submit():
        # Create a new Post instance when the form is submitted and validated
        tags = [Tag.query.filter_by(name=tag.strip()).first() or Tag(name=tag.strip()) for tag in form.tags.data.split(',')]
        post = Post(
            title=form.title.data,
            content=form.content.data,
            tags=tags
        )
        db.session.add(post)  # Add new post to the database session
        db.session.commit()  # Commit the session to save the post to the database
        flash('Your post has been created!', 'success')  # Flash a success message
        return redirect(url_for('forum.index'))  # Redirect to the index page
    return render_template('create_post.html', form=form)  # Render the post creation form

@bp.route('/reply/<int:post_id>', methods=['GET', 'POST'])
def reply_post(post_id):
    # Route for replying to a specific post
    form = ReplyForm()
    post = Post.query.get_or_404(post_id)  # Retrieve the post or return 404 if not found
    if form.validate_on_submit():
        # Create a new Reply instance when the form is submitted and validated
        reply = Reply(content=form.content.data, post_id=post_id)
        db.session.add(reply)  # Add new reply to the database session
        db.session.commit()  # Commit the session to save the reply to the database
        return redirect(url_for('forum.index'))  # Redirect to the index page
    return render_template('reply_post.html', form=form, post_id=post_id)  # Render the reply form

