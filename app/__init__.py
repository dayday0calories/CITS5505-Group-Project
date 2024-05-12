from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize database
db = SQLAlchemy()

# Initialize login manager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads'
    
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.logipn'  # Update this as per your Blueprint
    
    from app.blueprint.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from app.blueprint.pnr import pr as pr_blueprint
    app.register_blueprint(pr_blueprint)
    from app.blueprint.user import user as user_blueprint
    app.register_blueprint(user_blueprint)


    
    # Load the user with the login manager
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app

