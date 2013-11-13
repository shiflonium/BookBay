from hashlib import md5
from app import db
from app import app
from werkzeug import generate_password_hash, check_password_hash
import re
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, nullable=False)
    pwdhash = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    superuser = db.Column(db.Boolean, default=False)
    suspended = db.Column(db.Boolean, default=False)
    num_bids = db.Column(db.Integer, default=0)
    num_purchases = db.Column(db.Integer, default=0)
    credits = db.Column(db.Float, default=100.0)
    
    books = db.relationship('Book', backref='owner', lazy='dynamic')
    bids = db.relationship('Bid', backref='bidder', lazy='dynamic')
    book_comment = db.relationship('Book_Comments', backref='commenter', lazy='dynamic')
    
   
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

    def make_bid(self):
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


class Book(db.Model):
    """  """
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    information = db.Column(db.Text)
    price = db.Column(db.Float, default=1)
    date_added = db.Column(db.DateTime)
    
    # one book has many bids
    bids = db.relationship('Bid', backref='book', lazy='dynamic')
    commented_by = db.relationship('Book_Comments', backref='book', lazy='dynamic')

    def __repr__(self):
        return '<Book: %s owner: %s>' %(self.name, self.owner)


class Bid(db.Model):
    __tablename__ = "bid"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime)
    bid_price = db.Column(db.Integer, nullable=False)


class Book_Comments(db.Model):
    __tablename__ = "book_comments"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime)
    comment = db.Column(db.Text)
    pass


class User_Comments(db.Model):
    __tablename__ = "user_comments"
    id = db.Column(db.Integer, primary_key=True)
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commented_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    commenter = db.relationship('User',
            primaryjoin = (commenter_id==User.id),
            backref=db.backref('commenter', order_by=id))

    commented = db.relationship('User',
            primaryjoin = (commented_id==User.id),
            backref=db.backref('commented', order_by=id))
    
    timestamp = db.Column(db.DateTime)
    comment = db.Column(db.Text)

class User_Complaints(db.Model):
    __tablename__ = "user_complaints"
    id = db.Column(db.Integer, primary_key=True)
    complainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complained_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    complainer = db.relationship('User',
            primaryjoin = (complainer_id==User.id),
            backref=db.backref('complainer', order_by=id))

    complained = db.relationship('User',
            primaryjoin = (complained_id==User.id),
            backref=db.backref('complained', order_by=id))
    
    timestamp = db.Column(db.DateTime)
    comment = db.Column(db.Text)


if __name__ == '__main__':
    # won't run if you run from here, need to open ipython in virtualenv or .env/bin/python
    
    # add a user
    u1 = models.User(username='user1', email='user1@gmail.com', password='user1', first_name='user1', last_name='user1')
    u2 = models.User(username='user2', email='user2@gmail.com', password='user2', first_name='user2', last_name='user2')
    
    # add a book
    book1 = models.Book(owner=u1, name='book1', information ='book 1 info', price=22, date_added = datetime.utcnow())
    book2 = models.Book(owner=u1, name='book2', information ='book 2 info', price=21, date_added = datetime.utcnow())
    book3 = models.Book(owner=u2, name='book3', information ='book 3 info', price=10, date_added = datetime.utcnow())
    book4 = models.Book(owner=u2, name='book4', information ='book 4 info', price=15, date_added = datetime.utcnow())
    
    # add a bid
    bid1 = models.Bid(bidder=u1, book=book1, bid_price = 25, timestamp = datetime.utcnow())
    bid2 = models.Bid(bidder=u1, book=book2, bid_price = 125, timestamp = datetime.utcnow())
    bid3 = models.Bid(bidder=u2, book=book3, bid_price = 225, timestamp = datetime.utcnow())
    bid4 = models.Bid(bidder=u2, book=book4, bid_price = 325, timestamp = datetime.utcnow())
    
    # add a comment to book
    c1 = models.Book_Comments(commenter=u1, book=book1, comment='comment on book 1', timestamp = datetime.utcnow())
    c2 = models.Book_Comments(commenter=u1, book=book2, comment='comment on book 2', timestamp = datetime.utcnow())
    c3 = models.Book_Comments(commenter=u2, book=book3, comment='comment on book 3', timestamp = datetime.utcnow())
    c4 = models.Book_Comments(commenter=u2, book=book4, comment='comment on book 4', timestamp = datetime.utcnow())
    
    # add a comment to user
    d1 = models.User_Comments(commenter=u1, commented=u1, comment='comment on user1 by user1', timestamp = datetime.utcnow())
    d2 = models.User_Comments(commenter=u1, commented=u2, comment='comment on user2 by user1', timestamp = datetime.utcnow())
    d3 = models.User_Comments(commenter=u2, commented=u1, comment='comment on user1 by user 2', timestamp = datetime.utcnow())
    d4 = models.User_Comments(commenter=u2, commented=u2, comment='comment on user2 by user 2', timestamp = datetime.utcnow())
    
    # add a complaint to user
    e1 = models.User_Complaints(complainer=u1, complained=u2, comment='complaint on user2 from user1', timestamp = datetime.utcnow());
    e2 = models.User_Complaints(complainer=u1, complained=u2, comment='complaint on user2 from user1', timestamp = datetime.utcnow());
    e3 = models.User_Complaints(complainer=u1, complained=u2, comment='complaint on user2 from user1', timestamp = datetime.utcnow());
    e4 = models.User_Complaints(complainer=u2, complained=u1, comment='complaint on user1 from user2', timestamp = datetime.utcnow());
    e5 = models.User_Complaints(complainer=u2, complained=u1, comment='complaint on user1 from user2', timestamp = datetime.utcnow());


