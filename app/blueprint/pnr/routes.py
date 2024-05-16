from flask import render_template, request,jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user
from . import pr
from app.models.models import Post, Reply, db
from datetime import datetime
from .forms import PostForm
import openai

openai.api_key = 'sk-proj-H6JEx7SO3jRNYl34HD43T3BlbkFJ7VnFq93S41GPENddjF3E'

# Route for the post page
@pr.route('/view_posts')
def view_post():
    posts = Post.query.order_by(Post.created_at.desc()).all() # display the latest post first
    user = current_user
    for post in posts:
        last_reply = Reply.query.filter_by(post_id=post.id).order_by(Reply.created_at.desc()).first()
        if last_reply:  # Check if there is a reply
            post.last_replier_username = last_reply.user.username
            post.last_reply_date = last_reply.created_at
        else:
            post.last_replier_username = 'No replies'
            post.last_reply_date = None  # 
    return render_template('posts/view_posts.html', posts = posts, user = user)

# Route for the main page
@pr.route('/forums')
def forums():
    return render_template('forums.html')

# Route for detail page
@pr.route('/detail')
def detail():
    return render_template('auth/detail.html')


# Create post
@pr.route('/create-post', methods=['GET', 'POST'])
def create_post():
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('You must be logged in to view this page.')
        return redirect(url_for('auth.login'))  
        # Redirect them to the registration page

    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, category=form.category.data, content=form.content.data, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('pr.view_post'))  # Redirect to posts page
    return render_template('posts/create_post.html', form=form,user=current_user)



@pr.route('/detail/<int:post_id>')
def details(post_id):
    post = Post.query.get_or_404(post_id)  # Fetch the post or return 404 if not found
    post.views += 1  # Increment the view count
    db.session.commit()
    return render_template('posts/detail.html', post=post,user=current_user)


# Handle submit reply
@pr.route('/submit-reply/<int:post_id>', methods=['POST'])
def submit_reply(post_id):
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('You must be logged in to view this page.')
        return redirect(url_for('auth.login'))  
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
    return redirect(url_for('pr.details', post_id=post_id))  # Redirect back to the post detail page

# Route for AI Chatbot
@pr.route("/chat", methods=["GET", "POST"])
def chat():
    # If a POST request is received (i.e., when the user submits a question)
    if request.method == "POST":
        # Extract the question from the form data
        question = request.form["question"]
        
        # Generate a response using the GPT-3.5 Turbo model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}], # User's question
            temperature=0.6, 
            max_tokens=1000, 
        )
        # Redirect the user back to the chat page with the response as a query parameter
        return redirect(url_for("pr.chat", result=response.choices[0].message['content']))

    # If a GET request is received
    result = request.args.get("result")
    # Render the chatbot template with the response
    return render_template("posts/chatbot.html", result=result)

