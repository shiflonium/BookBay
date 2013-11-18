from app import db, models
from datetime import datetime
"""import sample data to db"""   

u1 = models.User(username='user1', email='user1@gmail.com', password='user1', first_name='user1', last_name='user1')
u2 = models.User(username='user2', email='user2@gmail.com', password='user2', first_name='user2', last_name='user2')

db.session.add(u1)
db.session.add(u2)
# add a book
book1 = models.Book(owner=u1, name='book1', information ='book 1 info', date_added = datetime.utcnow())
book2 = models.Book(owner=u1, name='book2', information ='book 2 info', date_added = datetime.utcnow())
book3 = models.Book(owner=u2, name='book3', information ='book 3 info', date_added = datetime.utcnow())
# this book is buyout only.
book4 = models.Book(owner=u2, name='book4', information ='book 4 info', buyout_price = 25, date_added = datetime.utcnow())

db.session.add(book1)
db.session.add(book2)
db.session.add(book3)
db.session.add(book4)
    # add a bid
bid1 = models.Bid(bidder=u1, book=book1, bid_price = 25, timestamp = datetime.utcnow())
bid2 = models.Bid(bidder=u1, book=book2, bid_price = 125, timestamp = datetime.utcnow())
bid3 = models.Bid(bidder=u2, book=book3, bid_price = 225, timestamp = datetime.utcnow())

db.session.add(bid1)
db.session.add(bid2)
db.session.add(bid3)
    # add a comment to book
c1 = models.Book_Comments(commenter=u1, book=book1, comment='comment on book 1', timestamp = datetime.utcnow())
c2 = models.Book_Comments(commenter=u1, book=book2, comment='comment on book 2', timestamp = datetime.utcnow())
c3 = models.Book_Comments(commenter=u2, book=book3, comment='comment on book 3', timestamp = datetime.utcnow())
c4 = models.Book_Comments(commenter=u2, book=book4, comment='comment on book 4', timestamp = datetime.utcnow())


db.session.add(c1)
db.session.add(c2)
db.session.add(c3)
db.session.add(c4)
    # add a comment to user
d1 = models.User_Comments(commenter=u1, commented=u1, comment='comment on user1 by user1', timestamp = datetime.utcnow())
d2 = models.User_Comments(commenter=u1, commented=u2, comment='comment on user2 by user1', timestamp = datetime.utcnow())
d3 = models.User_Comments(commenter=u2, commented=u1, comment='comment on user1 by user 2', timestamp = datetime.utcnow())
d4 = models.User_Comments(commenter=u2, commented=u2, comment='comment on user2 by user 2', timestamp = datetime.utcnow())

db.session.add(d1)
db.session.add(d2)
db.session.add(d3)
db.session.add(d4)
    # add a complaint to user
e1 = models.User_Complaints(complainer=u1, complained=u2, comment='complaint on user2 from user1', timestamp = datetime.utcnow());
e2 = models.User_Complaints(complainer=u1, complained=u2, comment='complaint on user2 from user1', timestamp = datetime.utcnow());
e3 = models.User_Complaints(complainer=u1, complained=u2, comment='complaint on user2 from user1', timestamp = datetime.utcnow());
e4 = models.User_Complaints(complainer=u2, complained=u1, comment='complaint on user1 from user2', timestamp = datetime.utcnow());
e5 = models.User_Complaints(complainer=u2, complained=u1, comment='complaint on user1 from user2', timestamp = datetime.utcnow());

db.session.add(e1)
db.session.add(e2)
db.session.add(e3)
db.session.add(e4)
db.session.add(e5)

# make transaction occur
db.session.commit()

# create the transaction
t = models.Transaction(seller=u2, buyer=u1, book=book4, amt_sold_for=book4.buyout_price, bought_out=True, time_sold = datetime.utcnow())
book = models.Book.query.filter_by(name='book4').first()
book.sold = True

db.session.add(t)
db.session.add(book)

#modify book status

#z = models.Book(owner=t.seller, sold=True)
# need to figure out how to dhtis nicely. 

db.session.commit()


