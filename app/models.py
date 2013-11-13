from hashlib import md5
from app import db
from app import app
from werkzeug import generate_password_hash, check_password_hash
import re
from datetime import datetime


# maybe use Mixin instead so no need to create
# the methods

#complaints = db.Table('complaints',
#        db.Column('complainer_id', db.Integer, db.ForeignKey('user.id')),
#        db.Column('complainee_id', db.Integer, db.ForeignKey('user.id')),
#        db.Column('text', db.String(256), default='EMPTY')
#        )

class User(db.Model):
    '''minimal'''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    pwdhash = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    superuser = db.Column(db.Boolean, default=False)
    suspended = db.Column(db.Boolean, default=False)
    num_bids = db.Column(db.Integer, default=0)
    num_purchases = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=100)
    
    books = db.relationship('Book', backref='owner', lazy='dynamic')
    bids = db.relationship('Bid', backref='bidder', lazy='dynamic')
    book_comment = db.relationship('Book_Comments', backref='commenter', lazy='dynamic')
    
#    complained = db.relationship('User',
#            secondary = complaints,
#            primaryjoin = (complaints.c.complainer_id == id),
#            secondaryjoin = (complaints.c.complainee_id == id),
#            backref = db.backref('complaints', lazy='dynamic'),
#            lazy = 'dynamic')
    
    # one user has many books
    #complaints = db.relationship('Complaint', backref='complainer', lazy='dynamic')
    
    def __init__(self, username, first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.set_password(password)
        #self.rating = float(0)

    def complain(self, user):
        self.complained.append(user)
        #self.complained.append('msg')
        return self
        pass


    def made_bid(self):
        """this method should be called after every bid. it should increment
        num_bids and then commit to database"""
        pass

    def made_purchase(self):
        """this method should be called after every sucessfull purchase. it should
        increment num_purchases and then commit changes to database"""
        pass
    
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


#class Complaint(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    text = db.Column(db.String(256))
#    timestamp = db.Column(db.DateTime)
#    complainer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    complainee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    
#    def __repr__(self):
#        return '<Complaint %r>' % (self.text)


class Book(db.Model):
    """  """
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(256))
    information = db.Column(db.String(256))
    price = db.Column(db.Integer) # leave as integer for now...
    # one book has many bids
    bids = db.relationship('Bid', backref='book', lazy='dynamic')
    commented_by = db.relationship('Book_Comments', backref='book', lazy='dynamic')


class Bid(db.Model):
    __tablename__ = "bid"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bid_price = db.Column(db.Integer)

class Book_Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment = db.Column(db.String(256))
    pass




class User_Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    commented_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment = db.Column(db.String(256))

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
    u2 = User(username='brian1', email='brian1', password='brian1', first_name='brian1', last_name='brian1')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    # won't run if you run from here, need to open ipython in virtualenv or .env/bin/python
    
    # add a user
    u1 = User(username='brian', email='brian', password='brian', first_name='brian', last_name='brian')
    # add a book
    p = models.Book(owner=u, name='book1', information ='ads', price=22)
    # add a bid
    bid = models.Bid(bidder=u1, book=p, bid_price = 25)
    # add a comment
    c = models.Book_Comment(commenter=u1, book=p, comment='comment')



