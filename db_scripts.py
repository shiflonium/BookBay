from app import db, models
from datetime import datetime

def add_user():
    u1 = models.User(
            username = 'user1',
            email = 'user1@gmail.com',
            password = 'user1',
            first_name = 'user1',
            last_name = 'user1',
            )
    u2 = models.User(
            username = 'user2',
            email = 'user2@gmail.com',
            password = 'user2',
            first_name = 'user2',
            last_name = 'user2'
            )
    u3 = models.User(
            username = 'user3',
            email = 'user3@gmail.com',
            password = 'user3',
            first_name = 'user3',
            last_name = 'user3'
            )
    q_u3 = models.User.query.filter_by(username='user3').first()
    q_u1 = models.User.query.filter_by(username='user1').first()
    q_u2 = models.User.query.filter_by(username='user2').first()
    if q_u1 is None:
        db.session.add(u1)
        db.session.commit()
    if q_u2 is None:    
        db.session.add(u2)
        db.session.commit()
    if q_u3 is None:
        db.session.add(u3)
        db.session.commit()
    
def add_book():
    u1 = models.User.query.filter_by(username = 'user1').first()
    u2 = models.User.query.filter_by(username = 'user2').first()

    # biddable books.
    book_c = models.Book(
            owner = u1,
            title = 'book_c',
            author = 'prof asdf',
            isbn = '978-3-16-148410-2',
            # this is the buyout price.
            price = 35,
            # bids start at 10.
            starting_bid = 10,
            current_bid = 10,
            # 2 day sale duration
            saleDuration = 2,
            publisher = 'a publisher',
            information = 'book 3 info',
            numOfPages = 500,
            lang = 'english',
            genre = 'erotica',
            edition = 4,
            condition = 'new',
            bookType = 'hardcover',
            biddable = True,
            buyable = True,
            date_added = datetime.utcnow()
            )
    # sellable books.
    book_a = models.Book(
            owner = u1,
            title = 'book_a',
            author = 'prof gertner',
            isbn = '978-3-16-148410-0',
            price = 10,
            saleDuration = 2,
            publisher = 'a publisher',
            information = 'book 2 info',
            numOfPages = 400,
            lang = 'english',
            genre = 'erotica',
            edition = 4,
            condition = 'new',
            bookType = 'hardcover',
            biddable = False,
            buyable = True
            )
    book_b = models.Book(
            owner = u2,
            title = 'book_b',
            author = 'prof grossberg',
            isbn = '978-3-16-148410-1',
            price = 20,
            saleDuration = 2,
            publisher = 'a publisher',
            information = 'book 2 info',
            numOfPages = 500,
            lang = 'french',
            genre = 'biography',
            edition = 6,
            condition = 'used',
            bookType = 'paperback',
            biddable = False,
            buyable = True
            )

    q_book_a = models.Book.query.filter_by(title='book_a', isbn= '978-3-16-148410-0').first()
    q_book_b = models.Book.query.filter_by(title='book_b', isbn= '978-3-16-148410-1').first()
    q_book_c = models.Book.query.filter_by(title='book_c', isbn= '978-3-16-148410-2').first()
    
    if q_book_c is None:
        db.session.add(book_c)
        db.session.commit()
    if q_book_a is None:
        db.session.add(book_a)
        db.session.commit()
    if q_book_b is None:
        db.session.add(book_b)
        db.session.commit()


def add_bid_transaction():
    """create a finished transaction for bid"""
    u1 = models.User.query.filter_by(username='user1').first()
    u2 = models.User.query.filter_by(username='user2').first()
    u3 = models.User.query.filter_by(username='user3').first()
    book_c = models.Book.query.filter_by(title='book_c', isbn= '978-3-16-148410-2').first()

    b1 = models.Bid(bidder=u3, book=book_c, bid_price = 20)
    book_c.current_bid = b1.bid_price

    q_b1 = models.Bid.query.filter_by(bidder=u3, book=book_c).first()
    if q_b1 is None:
        db.session.add(b1)
        db.session.add(book_c)
        db.session.commit()
    



def add_sell_transaction():
    """create a transaction for a book."""
    # query users.
    u1 = models.User.query.filter_by(username='user1').first()
    u2 = models.User.query.filter_by(username='user2').first()
    
    # query book_a and book_b
    book_a = models.Book.query.filter_by(title='book_a', isbn = '978-3-16-148410-0').first()
    book_b = models.Book.query.filter_by(title='book_b', isbn = '978-3-16-148410-1').first()
    # check whether user can afford.

    # create a transaction.
    # u2 buys book book_a from u1
    t1 = models.Transaction(seller=u1, buyer=u2, book=book_a, amt_sold_for=book_a.price, bought_out=True, time_sold = datetime.utcnow())
    # mark book_a as sold
    book_a.sold = True
    # deduct credits from u2 and apply credits to u1
    u2.credits = (u2.credits - book_b.price)
    u2.num_purchases += 1
    u1.credits = (u1.credits + book_b.price)
    
    q_t1 = models.Transaction.query.filter_by(seller=u1, buyer=u2, book=book_a).first()
    if q_t1 is None:
        db.session.add(t1)
        db.session.add(book_a)
        db.session.add(u2)
        db.session.add(u1)
        db.session.commit()

    # create another transaction
    t2 = models.Transaction(seller=u2, buyer=u1, book=book_b, amt_sold_for=book_b.price, bought_out=True, time_sold = datetime.utcnow())
    book_b.sold = True
    u1.credits = (u1.credits - book_a.price)
    u1.num_purchases += 1
    u2.credits = (u2.credits + book_a.price)

    q_t2 = models.Transaction.query.filter_by(seller=u2, buyer=u1, book=book_b).first()
    if q_t2 is None:
        db.session.add(t2)
        db.session.add(book_b)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()


if __name__ == '__main__':
    add_user()
    add_book()
    add_sell_transaction()
    add_bid_transaction()

