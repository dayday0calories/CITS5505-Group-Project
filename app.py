from app import create_app,db
from flask import Flask, request, render_template
from app.models.models import Post  

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

    return render_template('search_results.html', results=results, query=query)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
