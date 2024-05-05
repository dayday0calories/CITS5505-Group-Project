from app import db

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}'.format(self.username)

# Define the LoginHistory model    
class LoginHistory(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String[64], index = True)
    login_time = db.Column(db.DateTime)
    logout_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<LoginHistory {}>'.format(self.id)

# just test, add more if necessary


class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
