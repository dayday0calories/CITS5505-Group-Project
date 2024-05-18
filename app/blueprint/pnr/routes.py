from flask import render_template, request,jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user
from . import pr
from app.models.models import Post, Reply, db, User, Vote
from datetime import datetime
from .forms import PostForm
import openai
from app.blueprint.notifications.utils import create_notification, extract_mentions


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

        # 1.1 new feature: check for mentions and create notification
        mentions = extract_mentions(form.content.data) # Extract mentions from the post content
        for username in mentions:
            user = User.query.filter_by(username=username).first()
            if user:
                create_notification(
                    user_id=user.id, 
                    actor_id=current_user.id,
                    post_id=new_post.id, 
                    message=form.content.data[:50] + '...',
                    notification_type='mention'
                )
        # -end- 1.1

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

        #####################1.1 new feature
        # Create notification for the post author
        if current_user.id != post.user_id:  # Avoid notifying the user themselves
            create_notification(
                user_id=post.user_id, # the one who receives the notification
                actor_id=current_user.id, # the one who performs the notification
                post_id=post.id, 
                reply_id=reply.id, 
                message=reply_content[:50] + '...',
                notification_type='new_reply'
            )
        
        # Check for mentions and create notifications
        mentions = extract_mentions(reply_content)  # Extract mentions from the reply content
        for username in mentions:
            user = User.query.filter_by(username=username).first()
            if user and user.id != post.user_id:  # Avoid duplicate notification to the post author
                create_notification(
                    user_id=user.id, 
                    actor_id=current_user.id,
                    post_id=post.id, 
                    reply_id=reply.id, 
                    message=reply_content[:50] + '...',
                    notification_type='mention'
                )
        #######################1.1 end

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




#search function
@pr.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    search_type = request.args.get('search_type')

    # Get current user if logged in
    user = current_user if current_user.is_authenticated else None

    # Initialize results list
    results = []

    if query:

        # Ensure the query and search type are handled properly
        query = f"%{query}%"

        if search_type == 'Titles':
            # Search by post titles
             results = Post.query.filter(Post.title.ilike(query)).all()
        elif search_type == 'Descriptions':
            # Search by post descriptions
            results = Post.query.filter(Post.content.ilike(query)).all()
        else:
            # Search by both titles and descriptions
            results = Post.query.filter(
                Post.title.ilike(query) | Post.content.ilike(query)
            ).all()

    return render_template('posts/search_results.html', results=results, query=request.args.get('q'), user=user)  # Pass user to the template


#######################1.1 new features likes 
@pr.route('/vote/<string:type>/<int:id>/<string:action>', methods=['POST'])
@login_required
def vote(type, id, action):
    try:
        # Determine the item type (post or reply)
        if type == 'post':
            item = Post.query.get_or_404(id)
        elif type == 'reply':
            item = Reply.query.get_or_404(id)
        else:
            return jsonify({'success': False, 'error': 'Invalid type'}), 400

        # Check if the user has already voted on this item
        existing_vote = Vote.query.filter_by(
            user_id=current_user.id,
            post_id=id if type == 'post' else None,
            reply_id=id if type == 'reply' else None
        ).first()

        if existing_vote:
            if existing_vote.vote_type == action:
                # User is trying to vote the same way again, do nothing
                return jsonify({'success': False, 'error': 'You have already voted this way'}), 400
            
            # User is changing their vote
            if existing_vote.vote_type == 'like' and action == 'dislike':
                item.likes -= 1  # Remove the like
            elif existing_vote.vote_type == 'dislike' and action == 'like':
                item.likes += 1  # Remove the dislike

            # Remove the existing vote
            db.session.delete(existing_vote)
            db.session.commit()

            # Allow user to vote again
            return jsonify({'success': True, 'likes': item.likes, 'neutral': True})

        else:
            # Create a new vote record
            vote = Vote(
                user_id=current_user.id,
                post_id=id if type == 'post' else None,
                reply_id=id if type == 'reply' else None,
                vote_type=action
            )
            if action == 'like':
                item.likes += 1
            else:
                item.likes -= 1
            db.session.add(vote)

            db.session.commit()

            return jsonify({'success': True, 'likes': item.likes, 'neutral': False})

    except Exception as e:
        db.session.rollback()
        print(f"Error in vote route: {e}")  # Log the error
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

#######################
