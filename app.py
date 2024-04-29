from app import app, db
from app.models import User

if __name__ == '__main__':
    with app.app._context():
        db.create_all()
        app.run(debug=True)