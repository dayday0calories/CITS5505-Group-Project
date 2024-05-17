import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Secret key for session management
    SECRET_KEY = 'G5505-win'

    # Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    

    # Debug mode
    DEBUG = True

    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(basedir, 'flask_session')
    if not os.path.exists(SESSION_FILE_DIR):
        os.makedirs(SESSION_FILE_DIR)
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True