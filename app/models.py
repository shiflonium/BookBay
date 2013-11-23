from hashlib import md5
from app import db
from app import app
from werkzeug import generate_password_hash, check_password_hash
import re
from datetime import date, datetime
from sqlalchemy.orm import class_mapper, ColumnProperty


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
    # approved by admin? 
    apr_by_admin = db.Column(db.Boolean, default=False)
    num_bids = db.Column(db.Integer, default=0)
    num_purchases = db.Column(db.Integer, default=0)
    credits = db.Column(db.Float, default=100.0)
    # maybe we can have as our extra feature an analytics to tell admins
    # how long users are signed in. lol.
    # duration = last_login - last_logout
    last_login = db.Column(db.DateTime)
    last_logout = db.Column(db.DateTime)
    
    books = db.relationship('Book', backref='owner', lazy='dynamic')
    bids = db.relationship('Bid', backref='bidder', lazy='dynamic')
    book_comment = db.relationship('Book_Comments', backref='commenter', lazy='dynamic')
    
   
    def __init__(self, username, first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.set_password(password)

    # probably don't need this. should automatically do this action during a bid.
    def make_bid(self):
        """this method should be called after every bid. it should increment
        num_bids and then commit to database"""
        pass

    # probably don't need this. shuold automatically do this action during a transaction.
    def made_purchase(self):
        """this method should be called after every sucessfull purchase. it should
        increment num_purchases and then commit changes to database"""
        pass

    def is_suspended(self):
        """method for checking whether user is suspended."""
        return self.suspended

    def is_superuser(self):
        """method to check if user is super user."""
        return self.superuser

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
    title = db.Column(db.String(256))
    author = db.Column(db.String(256))
    isbn = db.Column(db.String(25))
    saleDuration = db.Column(db.Integer)
    publisher = db.Column(db.String(256))
    numOfPages = db.Column(db.Integer)
    lang = db.Column(db.String(25))
    genre = db.Column(db.String(25))
    edition = db.Column(db.Integer)
    condition = db.Column(db.String(25))
    bookType = db.Column(db.String(25))
    information = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    # simple way to implement books that are for auction with no buyout. 
    # no one should have 9,999 coins. can change value later.
    # user set starting bid price.
    # if a book can only be bought out and not auctioned, current_price will be set to price
    # if a book can be biddable
    biddable = db.Column(db.Boolean, nullable=False) # if True, book can be bid on.
    buyable = db.Column(db.Boolean, nullable=False)  # if True, book can be bought out. else: only can win through bid. 
    buyout_price = db.Column(db.Float)
    current_bid = db.Column(db.Float)
    starting_bid = db.Column(db.Float)
    date_added = db.Column(db.DateTime)

    image_name = db.Column(db.String(25))
    
    #could possibly use this to view all sold, avail books.
    sold = db.Column(db.Boolean, default=False)
    transac_id = db.relationship('Transaction', backref='book', lazy='dynamic')
    # one book has many bids
    bids = db.relationship('Bid', backref='book', lazy='dynamic')
    commented_by = db.relationship('Book_Comments', backref='book', lazy='dynamic')
    

    def columns(self):
        """Return the actual columns of a SQLAlchemy-mapped object"""
        return [prop.key for prop in class_mapper(self.__class__).iterate_properties
            if isinstance(prop, ColumnProperty)]


    def __init__(self, title=None, author=None, isbn=None, saleDuration=None, 
            publisher=None, numOfPages=None, lang=None,genre=None, edition=None,
            condition=None, bookType=None, information=None, rating=None,
            biddable=None, buyable=None, buyout_price=None, current_bid=None,
            starting_bid=None, date_added=None, owner=None, image_name=None):
        '''init method. so this only runs during the creation of book object.'''
        self.title = title
        self.author = author
        self.isbn = isbn
        self.saleDuration = saleDuration
        self.publisher = publisher
        self.numOfPages = numOfPages
        self.lang = lang
        self.genre = genre
        self.edition = edition
        self.condition = condition
        self.bookType = bookType
        self.information = information
        self.rating = rating
        self.biddable = biddable
        self.buyable = buyable
        self.buyout_price = buyout_price
        self.current_bid = current_bid
        self.starting_bid = starting_bid
        self.date_added = datetime.utcnow()
        self.owner = owner
        self.image_name = image_name
        
        if self.biddable is False and self.buyable is True:
            # if the book cannot be bid on, set the price of bids
            # equivalent to the value of the initial price.
            self.current_bid = self.buyout_price
            self.starting_bid = self.buyout_price
        
        elif self.biddable is True:
            # if the book CAN be bid on, make sure that:
            # the current bid is less than the buyout price(self.price)
            assert not (self.current_bid > self.buyout_price)
            # the starting bid is less than the buyout price(self.price)
            assert not (self.starting_bid > self.buyout_price)
            # the starting bid is less than the buyout price(self.price)
            assert self.starting_bid < self.buyout_price
            self.current_bid = self.starting_bid

    #GETTERS FOR ALL ATTRIBUITES FOR THE JINJA2 TEMPLATES
    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_isbn(self):
        return self.isbn

    def get_saleDuration(self):
        return self.saleDuration

    def get_publisher(self):
        return self.publisher

    def get_numOfPages(self):
        return self.numOfPages

    def get_language(self):
        return self.lang

    def get_genre(self):
        return self.genre

    def get_edition(self):
        return self.edition

    def get_condition(self):
        return self.condition

    def get_booktype(self):
        return self.bookType

    def get_information(self):
        return self.information

    def get_rating(self):
        return self.rating

    def get_biddable(self):
        return self.biddable

    def get_buyable(self):
        return self.buyable

    def get_buyout_price(self):
        return self.buyout_price

    def get_current_bid(self):
        return self.current_bid

    def get_starting_bid(self):
        return self.starting_bid

    def get_date_added(self):
        return self.date_added

    def get_owner(self):
        return self.owner_id

    def get_image_name(self):
        return self.image_name


    def get_seller(self):
        """returns user that sold book"""
        pass

    def get_buyer(self):
        """return user that bought the book, if there is a buyer"""
        pass
    
    def is_sold(self):
        """method that determines whether book is sold or not"""
        return self.sold

    def __repr__(self):
        return '<Book: %s owner: %s>' %(self.title, self.owner)


class Transaction(db.Model):
    """there will be two kinds of transactions, 'buy_out' and 'auctioned'. will
    be used to track transaction price, type."""
    
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'))
    amt_sold_for = db.Column(db.Float, nullable=False)
    bought_out = db.Column(db.Boolean, nullable=False)
    time_sold = db.Column(db.DateTime)
    
    seller = db.relationship('User',
            primaryjoin = (seller_id==User.id),
            backref=db.backref('seller', order_by=id))

    buyer = db.relationship('User',
            primaryjoin = (buyer_id==User.id),
            backref=db.backref('buyer', order_by=id))

    def __init__(self, seller=None, buyer=None, book=None,
            bid_id=None, amt_sold_for=None, bought_out=None, time_sold=None):
        
        self.seller = seller
        self.buyer = buyer
        self.book = book
        self.bid_id = bid_id
        self.amt_sold_for = amt_sold_for
        self.bought_out = bought_out
        self.time_sold = time_sold

    
    
    def __repr__(self):
        return '<Seller:%s, Owner:%s, book:%s, amt_sold_for:%s>' %( 
                self.seller, self.buyer, self.book.title, self.book.price )


class Bid(db.Model):
    __tablename__ = "bid"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    # change to buyer id.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime)
    bid_price = db.Column(db.Integer, nullable=False)

    def __init__(self, book, bidder, bid_price):
        self.bidder = bidder
        self.book = book
        self.bid_price = bid_price
        self.timestamp = datetime.utcnow()


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
    pass


