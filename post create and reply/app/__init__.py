from flask import Flask
from .models import db
from .routes import bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
    app.config['SECRET_KEY'] = 'CITS5505'
    db.init_app(app)
    app.register_blueprint(bp)
    return app
