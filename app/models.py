from hashlib import md5
from app import db
from app import app
from werkzeug import generate_password_hash, check_password_hash
import re
from datetime import date, datetime
import datetime as dt
from sqlalchemy.orm import class_mapper, ColumnProperty
from sqlalchemy import desc, update



class User(db.Model):
    """This table is used to store User model in the database.
    One User has MANY Book
    One User has MANY Book_Complaints
    One User has MANY Book_Comments
    One User has MANY Book_Ratings
    One User has MANY Bids
    
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, nullable=False)
    pwdhash = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    num_of_rating = db.Column(db.Integer, default =0)
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
    num_logins = db.Column(db.Integer, default = 0)
    
    su_message = db.relationship('SU_Messages', backref='msg_sender', lazy='dynamic')
    books = db.relationship('Book', backref='owner', lazy='dynamic')
    bids = db.relationship('Bid', backref='bidder', lazy='dynamic')
    book_comment = db.relationship('Book_Comments', backref='commenter', lazy='dynamic')
    book_complaint = db.relationship('Book_Complaints', backref='complainer', lazy='dynamic')
    book_ratings = db.relationship('Book_Ratings', backref='rater', lazy='dynamic')
    book_rec = db.relationship('Rec_Book', backref='recommender', lazy='dynamic')
       
   
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
    def get_username(self):
        """method for getting username"""
        return self.username

    def is_suspended(self):
        """method for checking whether user is suspended."""
        return self.suspended

    def is_superuser(self):
        """method to check if user is super user."""
        return self.superuser

    def set_password(self, password):
        """This method generates SHA-1 string from given input, password."""
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        """This method compares generated SHA-1 Hash to hash in database."""
        return check_password_hash(self.pwdhash, password)

    def is_authenticated(self):
        """returns False when Users are not logged in."""
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        """returns True if User is not logged in."""
        return False

    def get_id(self):
        """returns User's primary key id."""
        return unicode(self.id)

    def get_credit(self):
        """returns the credits A user has."""
        return self.credits

    def get_num_purch(self):
        """returns the number of book purchases a user has made."""
        return self.num_purchases

    def get_avg_rating(self):
        """returns average rating of user."""
        if self.num_of_rating == 0:
            return 0
        else:
            avg = (self.rating / self.num_of_rating)*2
            rounded = round(avg)
            final = rounded/2
            return final

    def increment_login(self):
        """increments User login_count"""
        self.num_logins += 1
        #db.session.commit()

    def increment_purchases(self):
        """increments Users num_purchases count"""
        self.num_purchases += 1
        #db.session.commit()

    def times_logged_in(self):
        """returns number of times User has logged in"""
        return self.num_logins

    def is_approved(self):
        """returns True/False if User is approved by SuperUser"""
        return self.apr_by_admin

    def has_enough_credits(self, book_price):
        """returns True/False if User has enough credits to to purchase Book."""
        if self.credits < book_price:
            return False
        else:
            return True

    def return_credits(self):
        """returns User's credits"""
        return self.credits

    def num_books_sold(self):
        """returns number of books User has SOLD."""
        trans = Transaction.query.filter_by(seller = self).all()
        return len(trans)

    def num_user_comments_made(self):
        """returns number of User_Comments User has made."""
        user_comments = User_Comments.query.filter_by(commenter = self).all()
        return len(user_comments)

    def num_book_comments_made(self):
        """returns number of Book_Comments User has made."""
        book_comments = Book_Comments.query.filter_by(user_id = self.id).all()
        return len(book_comments)

    def num_user_comments_directed(self):
        """returns number of User_Comments directed towards User."""
        user_comments = User_Comments.query.filter_by(commented = self).all()
        return len(user_comments)

    def add_credits(self, amount):
        """method to add credits to a User."""
        self.credits = self.credits + float(amount)
        db.session.commit()
        
    def subtract_credits(self, amount):
        """method to subtract credits from a User"""
        self.credits = self.credits - float(amount)
        db.session.commit()

    def send_msg(self, status, text):
        """method creates message to be seen by SuperUser"""
        msg = SU_Messages(
                msg_sender = self,
                status = status,
                message = text,
                timestamp = datetime.utcnow()
                )
        db.session.add(msg)
        db.session.commit()
        pass
    
    def create_comment(self, user_id, text):
        """method to create a User_Comment.
        parameters: target user_id and commment
        """
        # user_id = session['user_id']
        commenter = User.query.filter_by(id = user_id).first()
        comment = User_Comments(
                commenter = commenter,
                commented = self,
                comment = text,
                timestamp = datetime.utcnow()
                )
        db.session.add(comment)
        db.session.commit()
        pass

    def get_username(self):
        return self.username
        

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
    isbn = db.Column(db.String(25))#
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
    num_of_rating = db.Column(db.Integer, default=0)
    suspended = db.Column(db.Boolean, default=False)

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
    complaints = db.relationship('Book_Complaints', backref='book', lazy='dynamic')
    book_ratings = db.relationship('Book_Ratings', backref='book', lazy='dynamic')

    

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
        # force starting_bid to be current_bid
        self.current_bid = current_bid
        self.starting_bid = starting_bid
        self.date_added = datetime.utcnow()
        self.owner = owner
        self.image_name = image_name
        
        
        '''
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
        '''
           #GETTERS FOR ALL ATTRIBUITES FOR THE JINJA2 TEMPLATES

    def get_id(self):
        return self.id

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
        return self.owner_id

    def get_buyer(self):
        """return user that bought the book, if there is a buyer"""
        pass
    def is_suspended(self):
        """method for checking whether user is suspended."""
        return self.suspended

    def is_sold(self):
        """method that determines whether book is sold or not"""
        if self.sold == True:
            return True
        else:
            return False

    def get_avg_rating(self):
        """returns average rating of book."""
        if self.num_of_rating == 0:
            return 0
        else:
            avg = (self.rating / self.num_of_rating)*2
            rounded = round(avg)
            final = rounded/2
            return final

    def get_expr_date(self):
        """return date when book should run out of time.
        Assuming that saleDuration is in days. """
        return self.date_added + dt.timedelta(days = self.saleDuration)

    def is_book_expr(self):
        """returns True/False whether or not book is passed expiration date.
        Used to remove/create transaction for books. """
        expr_date = self.get_expr_date()
        now = datetime.utcnow()
        #print "expr_date: %s  now: %s" % (expr_date, now)
        if expr_date <= now:
            return True
        else:
            return False
        
    def until_expire_in_mins(self):
        """returns time until book expires in minutes"""
        expr_date = self.get_expr_date()
        delta = expr_date - datetime.utcnow()
        delta_in_mins = int(delta.total_seconds() / 60 )
        return delta_in_mins

    def until_expire_in_hrs(self):
        """returns time until book expires in hours"""
        return (self.until_expire_in_mins() / 60)

    def have_bids(self):
        """returns True if book has bids"""
        return not(self.not_have_bids())
    
    def not_have_bids(self):
        """returns True if book does NOT have bids"""
        book_bids = Bid.query.filter_by(book_id = self.id).all() 
        if len(book_bids) == 0:
            return True
        else:
            return False

    def create_comment(self, user_id, text):
        """method to create a book comment.
        parameters: commenter user_id and message."""
        commenter = User.query.filter_by(id = user_id).first()

        comment = Book_Comments(
                commenter = commenter,
                book = self,
                comment= text,
                timestamp = datetime.utcnow())
        db.session.add(comment)
        db.session.commit()

    def create_complaint(self, user_id, text):
        """method to create a book complaint.
        parameters: complainer user_id and message."""
        user = User.query.filter_by(id = user_id).first()
        
        book_complaint = Book_Complaints(
                complainer = user,
                book = self,
                comment = text,
                timestamp = datetime.utcnow()
                )
        db.session.add(book_complaint)
        db.session.commit()

    def create_rating(self, user_id, rating):
        """method to create rating for book.
        paramters: rater user_id, rating"""
        user = User.query.filter_by(id = user_id).first()

        rating_exists = Book_Ratings.query.filter_by(rater = user).first()
        # if user has not rated the book
        if not rating_exists:
            rating = Book_Ratings(
                    rater = user,
                    book = self,
                    rating = rating,
                    timestamp = datetime.utcnow()
                    )
            db.session.add(rating)
            db.session.commit()

    
    def create_bid(self, session_id, bid_amount=None):
        """creates a bid transaction for the book
        user_session variable passed in from views. returns user_id."""
        # get the user
        user = User.query.filter_by(id = session_id).first()
        if user is None:
            raise Exception('create bid error. user returned none. should not happen.')
        
        # check user has enough credits
        if user.credits < (self.current_bid + 1.0):
            print 'user.credits:%s' % user.credits
            print 'self.current_bid:%s' % self.current_bid
            # temporary
            return 'you do not have enough credits to bid'
        else:
            # if bid_amount is not passed in, automatically bid + 1.0
            try:
                user_bid_amount = float(bid_amount)
            except ValueError:
                # this executes if user does not input a value.
                # defaults to 1.0 greater than current_bid
                print 'catching ValueError'
                user_bid_amount = self.current_bid + 1.0

            if (user_bid_amount < user.credits) and (user_bid_amount > self.current_bid):
                # create the bid transaction
                bid = Bid(bidder = user, book=self, bid_price = user_bid_amount)
                self.current_bid = user_bid_amount
                # increment bid count for user
                db.session.add(bid)
                # update book current_bid
                user.num_bids += 1
                db.session.commit()

    def get_highest_bid(self):
        """returns bid object with highest bid amount for book."""
        bid = Bid.query.filter_by(book=self).order_by(desc(Bid.bid_price)).first()
        return bid

    def is_approved_by_seller(self):
        book_to_approve = Buyer_transaction_approval.query.filter_by(book_id = self.id).first()
        if book_to_approve != None:
            return book_to_approve.need_to_approve
        else:
            return False

    def create_buy_now_transcation(self, buyer):
        """creates a buy now transaction. Used when a User chooses to click
        'buy now' for a book. automatically purchasing the book and creating
        transaction for the user/book."""
        seller = self.owner
        book_cost = self.buyout_price

        if not(buyer.has_enough_credits(book_cost)):
            return 'user cannot afford this book'
    
        transac_time = datetime.utcnow()

        trans = Transaction(seller=seller, buyer=buyer,book=self,
            amt_sold_for=book_cost, bought_out=True,time_sold=transac_time)
        db.session.add(trans)

        buyer.num_purchases += 1
        buyer.subtract_credits(book_cost)
        seller.add_credits(book_cost)
        self.sold = True
        db.session.commit()
        s = "*" * 10
        print "%s %s Transaction Created %s" % (s, transac_time, s)
        print "%s sold book: %s to %s @ buy_now price: %s" % (seller.username, self.title, buyer.username, self.buyout_price)

    
    def create_bid_win_transaction(self):
        """
        creates a transaction when a User wins book by bidding.
        Triggers when either book expires and has bids or when
        book owner decides to accept highest bid amount.
        1. create transaction object
        2. modify book.sold = True 
        3. give credits to seller and subtract credits from buyer
        """
        highest_bid = self.get_highest_bid()
        seller = self.owner
        buyer = highest_bid.bidder
        book_cost = self.current_bid
        transac_time = datetime.utcnow()

        trans = Transaction(seller=seller, buyer=buyer, book=self,
                bid_id=highest_bid.id, amt_sold_for=book_cost,
                bought_out=False, time_sold=transac_time )
        db.session.add(trans)
        
        buyer.num_purchases += 1
        buyer.subtract_credits(book_cost)
        seller.add_credits(book_cost)
        self.sold = True
        db.session.commit()
        s = "*" * 10
        print "%s %s Transaction Created %s" % (s, transac_time, s)
        print "%s sold book: %s to %s @ price: %s" % (seller.username, self.title, buyer.username, self.current_bid)

    


    def __repr__(self):
        return '<Title: %s Owner: %s>' %(self.title, self.owner)

class Transaction(db.Model):
    """
    Transaction are created when a Book is sold by buying out or by bidding.
    there will be two kinds of transactions, 'buy_out' and 'auctioned'. will
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
    """Table used to track ALL bids created for ALL books."""
    __tablename__ = "bid"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    # change to buyer id.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime)
    bid_price = db.Column(db.Float, nullable=False)


    def __init__(self, book, bidder, bid_price):
        self.bidder = bidder
        self.book = book
        self.bid_price = bid_price
        self.timestamp = datetime.utcnow()


class Book_Comments(db.Model):
    """Table used to track ALL book comments for ALL Books created by User"""
    __tablename__ = "book_comments"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime)
    comment = db.Column(db.Text)

    def __repr__(self):
        return "comment_id: %s book_id: %s" % (self.id, self.book_id)

class Book_Complaints(db.Model):
    """Table used to track ALL book complaints for ALL Books created by User"""
    __tablename__ = "book_complaints"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime)
    comment = db.Column(db.Text)

    def __repr__(self):
        return "user_id: %s book_id: %s" % (self.user_id, self.book_id)

class Book_Ratings(db.Model):
    """Table used to track ALL book ratings for ALL books created by User"""
    __tablename__ = "book_ratings"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime)

# class User_Ratings(db.Model):
#     __tablename__ = "user_ratings"
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False, nullable=False)
#     rating = db.Column(db.Integer, nullable=False)
#     timestamp = db.Column(db.DateTime)


class User_Comments(db.Model):
    """Table used to track ALL User Comments by a User """
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


class SU_Messages(db.Model):
    """Table used to track ALL messages sent to SuperUser."""
    __tablename__ = 'su_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)


class User_Complaints(db.Model):
    """Table used to track ALL User Complaints created by a User."""
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
    active = db.Column(db.Boolean, default=True)    
    timestamp = db.Column(db.DateTime)
    comment = db.Column(db.Text)


class Rec_Book(db.Model):
    __tablename__ = "rec_book"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genre = db.Column(db.Text)


class Buyer_transaction_approval(db.Model):
    __tablename__ = 'buyer_transaction_approval'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    need_to_approve = db.Column(db.Boolean, nullable=False)   

    def get_book_name(self):
        return Book.query.filter_by(id = self.book_id).first().title

    def get_book_id(self):
        return self.book_id

if __name__ == '__main__':
    pass


