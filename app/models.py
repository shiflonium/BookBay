from hashlib import md5
from app import db
from app import app
from werkzeug import generate_password_hash, check_password_hash
import re

# maybe use Mixin instead so no need to create
# the methods
class User(db.Model):
    '''minimal'''
    id = db.Column(db.Integer, primary_key=True)
    # use username as checker
    username = db.Column(db.String(64), unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    pwdhash = db.Column(db.String(100))
    # 1-5 star personal rating
    rating = db.Column(db.Float, default=0.0)
    superuser = db.Column(db.Boolean, default=False)
    suspended = db.Column(db.Boolean, default=False)
    num_bids = db.Column(db.Integer, default=0)
    num_purchases = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=100)
    # one user has many books
    books = db.relationship('Book', backref='owner', lazy='dynamic')
    #bids = db.relationship('Bid', backref='bidder', lazy='dynamic')
    
    # one user has many complaints
    #complaints = db.relationship('Complaint', backref='user', lazy='dynamic')

    def __init__(self, username, first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.set_password(password)
        #self.rating = float(0)

    def is_suspended(self):
        """method for checking whether user is suspended."""
        return False
    
    
    def is_superuser(self):
        """method to check if user is super user."""
        return False
    
    
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
        #return '<User %r>' % (self.username)
        return self.username


class Book(db.Model):
    """  """
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(256))
    information = db.Column(db.String(256))
    comments = db.Column(db.String(256))
    price = db.Column(db.Integer) # leave as integer for now...
    # one book has many bids
    bids = db.relationship('Bid', backref='book', lazy='dynamic')


class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bid_price = db.Column(db.Integer)


#class Book_Comments(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    comment = db.Column(db.String(256))
#    pass


#class User_Comments(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#
#    pass

# many to many relationship
# many books can have many bids...i think..

#class Complaint(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    complainer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    complainee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    message = db.Column(db.String(256))


if __name__ == '__main__':
    pass



