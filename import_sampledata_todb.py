from app import db, models
from datetime import datetime
"""import sample data to db"""   

u1 = models.User(username='user1', email='user1@gmail.com', password='user1', first_name='user1', last_name='user1')
u2 = models.User(username='user2', email='user2@gmail.com', password='user2', first_name='user2', last_name='user2')

db.session.add(u1)
db.session.add(u2)
# add a book
book1 = models.Book(owner=u1, name='book1', information ='book 1 info', price=22, date_added = datetime.utcnow())
book2 = models.Book(owner=u1, name='book2', information ='book 2 info', price=21, date_added = datetime.utcnow())
book3 = models.Book(owner=u2, name='book3', information ='book 3 info', price=10, date_added = datetime.utcnow())
book4 = models.Book(owner=u2, name='book4', information ='book 4 info', price=15, date_added = datetime.utcnow())

db.session.add(book1)
db.session.add(book2)
db.session.add(book3)
db.session.add(book4)
    # add a bid
bid1 = models.Bid(bidder=u1, book=book1, bid_price = 25, timestamp = datetime.utcnow())
bid2 = models.Bid(bidder=u1, book=book2, bid_price = 125, timestamp = datetime.utcnow())
bid3 = models.Bid(bidder=u2, book=book3, bid_price = 225, timestamp = datetime.utcnow())
bid4 = models.Bid(bidder=u2, book=book4, bid_price = 325, timestamp = datetime.utcnow())

db.session.add(bid1)
db.session.add(bid2)
db.session.add(bid3)
db.session.add(bid4)
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


try:
    db.session.commit()
except:
    print 'something went wrong'


