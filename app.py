from app import create_app,db
from flask import Flask, request, render_template
from app.models.models import Post
from flask_login import current_user
app = create_app()

#just say hi
@app.route('/')
def index():
    return "Hello, World!"

#search function
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    search_type = request.args.get('search_type')

    # Get current user if logged in
    user = current_user if current_user.is_authenticated else None

    if query:
        if search_type == 'Titles':
            results = Post.query.filter(Post.title.ilike(f'%{query}%')).all()
        elif search_type == 'Descriptions':
            results = Post.query.filter(Post.content.ilike(f'%{query}%')).all()
        else:
            results = Post.query.filter(
                (Post.title.ilike(f'%{query}%')) | (Post.content.ilike(f'%{query}%'))
            ).all()
    else:
        results = []

    return render_template('search_results.html', results=results, query=query, user=user)  # Pass user to the template

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)