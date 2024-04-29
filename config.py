import os

class Config:
    # Secret key for session management
    SECRET_KEY = 'G5505-win'

    # Database URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

    # Debug mode
    DEBUG = True