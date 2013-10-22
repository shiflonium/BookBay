from hashlib import md5
from app import db
from app import app
from werkzeug import generate_password_hash, check_password_hash
import re

# maybe use Mixin instead so no need to create
# the methods
class User(db.Model):
    '''minimal'''
    id = db.Column(db.Integer, primary_key = True)
    # use username as checker
    username = db.Column(db.String(64), unique = True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique = True)
    pwdhash = db.Column(db.String(100))
    # 1-5 star personal rating
    #rating = db.Column(db.Float)

    def __init__(self, username, first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.set_password(password)
        self.rating = float(0)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)
