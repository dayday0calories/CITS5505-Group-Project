import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for session management
    SECRET_KEY = 'G5505-win'

    # Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug mode
    DEBUG = True