from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from models import User, Book, Transaction, Bid, User_Comments, Book_Comments, User_Complaints, SU_Messages
from forms import SignUpForm, LoginForm, ChangePassword, ChangePersonalDetails, SearchForm, sellForm, BidForm, PostForm, SUForm, ComplainForm
from werkzeug import generate_password_hash, check_password_hash, secure_filename
from datetime import datetime
from sqlalchemy import desc, update
import os
import random
import string
import datetime as dt


'''
This function defines the files which are allowed to be uploaded
'''
def allowed_file(filename):
    print app.config['UPLOAD_FOLDER']
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(id):
    '''method used by Flask-Login to get 
    key for login user. query.get is for primary keys'''
    return User.query.get(int(id))


@app.before_request
def before_request():
    '''this is executed before every routing request.
    g is a global user variable that is automatically
    passed in to templates. i.e. {{% if g.user.is_anonymous %}} '''
    # do something before each request
    g.user = current_user
    if g.user.is_authenticated():
        db.session.add(g.user)
        db.session.commit()
        if g.user.is_suspended():
            flash("Your Account has been SUSPENDED. Please wait for an admin to take action.\
                    You can still browse books as a public user.")
            logout()
            return render_template('home.html')
        if g.user.is_approved() == False:
            flash("Your Account has not been approved by Admin, Please wait for Admin action.\
                    You may browse books as public user.")
            logout()
            return render_template('home.html')

# executed by do_book_removal_and_purchase_checking
def check_book_expr_and_has_bids():
    """this function executes when a book is expired and has bidders. should sell
    book to highest bidder. if a book expires and has bids, take the highest bid
    amount and sell it to that user.
    
    """
    print 'CHECKING IF THERE ARE ANY EXPIRED BOOKS WITH BIDS'
    all_books = Book.query.all()


    pass
# executed by do_book_removal_and_purchase_checking
def check_book_expr_and_no_bids():
    """easiest way to keep db updated.... this will run anytime ANY user clicks on anything
    only doing this because it's for a class project lol.
    - Books with no bidder are automatically removed from the system after the stated deadline.
    adding print statements for debugging
    """
    check_book_expr_and_has_bids()
    all_books = Book.query.all()
    print "checking %s books." % (len(all_books))
    for book in all_books:
        # if book is expired and does not have any bids
        print "%s expired? %s" % (book.title, book.is_book_expr())
        print "%s have_bids? %s" % (book.title, book.is_book_expr())
        if book.is_book_expr() and book.not_have_bids():
            # remove foreign key constraints, in this case it should only be comments
            comments = Book_Comments.query.filter_by(book_id = book.id).all()
            print len(comments)
            print comments
            for comment in comments:
                print "deleting comment: %s" % comment
                db.session.delete(comment)
                db.session.commit()
            print "deleting book: %s" % book
            db.session.delete(book)
            db.session.commit()
        else:
            print "Book:%s ISBN: %s  expires in %s minutes." % (book.title, book.isbn, book.until_expire_in_mins())
            print "Book:%s ISBN: %s  expires in %s hours." % (book.title, book.isbn, book.until_expire_in_hrs())

@app.before_request
def do_book_removal_and_purchase_checking():
    """this executes the functions that figure out what to do when books are
    1. expired and have no bids => remove them
    2. expired and HAS bids => create a transaction and make book sold."""
    check_book_expr_and_no_bids()
    check_book_expr_and_has_bids()


@app.route('/', methods = ['GET', 'POST'], defaults = {'path':''})
@app.route('/<path:path>', methods = ['GET', 'POST'])
def request_for_search(path):
    search_data = None 
    if request.method == 'GET':
        if request.args.get('user_check'):
            search_data = request.args.get('user_search_field')
            session['parameter'] = search_data
            if search_data != None:
                full_url = url_for('search')
                return redirect(full_url)
        else:
            search_data = request.args.get('book_search_field')
            session['parameter'] = search_data
            if search_data != None:
                full_url = url_for('search_book')
                return redirect(full_url)
            

@app.route('/', methods = ['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST' and form.validate():
        u = User(
                form.username.data,
                form.first_name.data,
                form.last_name.data,
                form.email.data,
                form.password.data
                )
        db.session.add(u)
        db.session.commit()
        # adding email token to session, might use later.
        #session['email'] = u.email
        return redirect(url_for('home'))
    # this executes if GET request
    return render_template('signup.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        # if username is valid on submit, login the user
        user = User.query.filter_by(username = form.username.data).first()
        login_user(user)

        # add timestamp for last_login
        user.last_login = datetime.utcnow()
        user.increment_login()
        # put user_id in session for later use
        session['user_id'] = user.id
        db.session.add(user)
        db.session.commit()
        
        #flash("logged in sucessfully :)")
        return redirect(request.args.get('next') or url_for('profile'))
        #return redirect(url_for('profile'))
    else:
        #flash("incorrect password")
        return render_template('login.html',form=form)
    return render_template("login.html",form=form)

@app.route('/signout')
@login_required
def logout():
    user = User.query.filter_by(id = session['user_id']).first()
    user.last_logout = datetime.utcnow()
    # put user_id in session for later use
    db.session.commit()
    # delete session created during login
    del session['user_id']
    logout_user()
    return redirect(url_for('home'))



@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    #return 'this is the profile page, if you can see this, you are logged in'
    form1 = ChangePassword()
    form2 = ChangePersonalDetails()
    return render_template('profile.html', form1=form1, form2=form2)
 

@app.route('/profile/<username>', methods=['POST', 'GET'])
@login_required
def show_user(username):
    # add comment form
    # add rating form
    user = User.query.filter_by(username=username).first()
    if user is None:
        #temp
        return 'user does not exist'
    return render_template('browse_user.html', user=user)
    


@app.route('/changePassword', methods = ['POST'])
@login_required
def changePass():
    '''
    Chage user password
    '''
    u = request.form['username']
    oldPass = request.form['oldPassword']
    newPass = request.form['newPassword']
    newPass2 = request.form['newPassword2']
    user = User.query.filter_by(username = str(u)).first()

    if check_password_hash(user.pwdhash, oldPass):
        if newPass == newPass2:         #Case everything is right
            newHash = generate_password_hash(newPass)
            user.pwdhash = newHash
            db.session.commit()
            redirect(url_for('profile'))


        else: 
            return "Passwords doesn't match, please click the back button and try again."

    else:
        return "Wrong Password, please use the back button."

    return redirect(url_for('profile'))
    user = User.query.filter_by(username = u).first()
    #return request.form['username']


@app.route('/changePersonalDetails', methods = ['POST'])
@login_required
def changeDetails():
    '''
    Change first and last name in the database
    '''
    u = request.form['username']
    user = User.query.filter_by(username = str(u)).first()
    firstName = request.form['first_name']
    lastName = request.form['last_name']
    if firstName:
        user.first_name = firstName
    if lastName:
        user.last_name = lastName
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/admin/transaction_history', methods=['GET', 'POST'])
@login_required
def transaction_history():
    user = User.query.filter_by(id = session['user_id']).first()
    if user.superuser == True:
        trans = Transaction.query.all()
        return render_template('transaction_history.html', trans=trans)
    else:
        return redirect(url_for('home'))

@app.route('/admin/remove_user/<user_id>')
@login_required
def remove_user(user_id):
    user = User.query.filter_by(id = session['user_id']).first()
    if user.superuser == False:
        return redirect(url_for('home'))
    # write this
    return redirect(url_for('home'))

@app.route('/admin/suspend_user/<user_id>')
@login_required
def suspend_user(user_id):
    user = User.query.filter_by(id = session['user_id']).first()
    if user.superuser == False:
        return redirect(url_for('home'))
    u = User.query.filter_by(id = user_id).first()
    u.suspended = True
    db.session.commit()
    return redirect(url_for('get_all_users'))

@app.route('/admin/unsuspend_user/<user_id>')
@login_required
def unsuspend_user(user_id):
    user = User.query.filter_by(id = session['user_id']).first()
    if user.superuser == False:
        return redirect(url_for('home'))
    u = User.query.filter_by(id = user_id).first()
    u.suspended = False
    db.session.commit()
    return redirect(url_for('get_all_users'))


@app.route('/admin/approve_user/<user_id>')
@login_required
def approve_user(user_id):
    user = User.query.filter_by(id = session['user_id']).first()
    if user.is_superuser() == False:
        return redirect(url_for('home'))
    u = User.query.filter_by(id = user_id).first()
    u.apr_by_admin = True
    db.session.commit()
    return redirect(url_for('get_all_users'))

@app.route('/admin/remove_book/<book_id>')
@login_required
def remove_book(book_id):
    user = User.query.filter_by(id = session['user_id']).first()
    if user.superuser == False:
        return redirect(url_for('home'))
    #idk how to cascade so doing this manually
    book = Book.query.filter_by(id = book_id).first()
    bids = Bid.query.filter_by(book_id = book.id).all()
    comments = Book_Comments.query.filter_by(book_id = book.id).all()
    # delete all comments
    for comment in comments:
        db.session.delete(comment)
    # delete all bids
    for bid in bids:
        db.session.delete(bid)
    # delete book
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('browse'))

@app.route('/admin/bid_history', methods=['GET', 'POST'])
@login_required
def bid_history():
    user = User.query.filter_by(id = session['user_id']).first()
    if user.superuser == True:
        bids = Bid.query.order_by(desc(Bid.timestamp)).all()
        return render_template('bid_history.html', bids=bids)
    else:
        return redirect(url_for('home'))

@app.route('/admin/su_msg_list', methods=['GET','POST'])
@login_required
def su_msg_list():
    msgs = SU_Messages.query.order_by(desc(SU_Messages.timestamp)).all()

    return render_template("view_msgs.html", msgs=msgs)


@app.route('/admin/user_list', methods=['GET', 'POST'])
@login_required
def get_all_users():
    user = User.query.filter_by(id = session['user_id']).first()

    # setting to false for now
    if user.superuser == True:
        user_data = User.query.all()
        return render_template('user_list.html',
                user_data = user_data
                )
    else:
        return redirect(url_for('home'))

@app.route('/view_profile/<user_id>', methods = ['GET', 'POST'])
@login_required
def view_profile(user_id):
    """PUBLIC PROFILE"""
    #username_from_get = request.args.get()
    form = PostForm()
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return 'user does not exist'
    if request.method == 'POST' and form.validate_on_submit():
        text = request.form['post']
        user.create_comment(session['user_id'], text)
    comments = User_Comments.query.filter_by(commented = user).order_by(desc(User_Comments.timestamp)).all()
    return render_template('view_profile.html',
            user_id = user_id,
            user = user,
            form = form,
            comments = comments
            )

@app.route('/personal_profile/<user_id>', methods=['GET', 'POST'])
@login_required
def personal_profile(user_id):
    """PRIVATE PROFILE"""
    user = User.query.filter_by(id = session['user_id']).first()
    if user.is_superuser() == False:
        # check if someone else is trying to access profile
        if int(user_id) != int(session['user_id']):
            print "user_id: %s  session['user_id']:%s" % (user_id, session['user_id'])
            return redirect(url_for('home'))
    view_user = User.query.filter_by(id = user_id).first()
    
    comments_recieved = User_Comments.query.filter_by(commented = view_user).order_by(desc(User_Comments.timestamp)).all()
    comments_made = User_Comments.query.filter_by(commenter = view_user ).order_by(desc(User_Comments.timestamp)).all()
    
    return render_template('personal_profile.html',
            comments_recieved = comments_recieved,
            comments_made = comments_made,
            user=view_user)

@app.route('/send_msg', methods=['GET', 'POST'])
@login_required
def send_msg():
    form = SUForm()
    user = User.query.filter_by(id = session['user_id']).first()
    if request.method == 'POST' and form.validate_on_submit():
        msg = form.message.data
        status = form.status.data
        #msg = request.form['msg']
        #status = request.form['status']

        user.send_msg(status=status, text=msg)
        flash ('message sent to su')
        return redirect(url_for('home'))
    return render_template('send_msg.html', form=form)





@app.route('/search_users', methods = ['GET', 'POST'])
def search():
    usernames = []
    search_data =""
    search_data = session['parameter']
    query = User.query.filter(User.username.like("%"+search_data+"%")).all()
    usernames=[u for u in query]
    return render_template("search.html", query = usernames, results = search_data)


@app.route('/search_books', methods = ['GET','POST'])
def search_book():
    table = Book()
    books = []
    search_data = ""
    search_data = session['parameter']
    query = Book.query.filter(Book.title.like("%"+search_data+"%"))
    books = [b for b in query]
    return render_template("search_books.html", query = query, results = search_data)    


@app.route('/sell', methods = ['GET', 'POST'])
@login_required
def sell():
    form = sellForm()
    



    if (request.method == 'POST') and form.validate_on_submit(): 

        #DETERMINE IF USER HAVE ENOUGH CREDIT TO SELL THE BOOK

        #GET USER ID
        username = request.form['username']
        user = User.query.filter_by(username = str(username)).first()
        userid = user.id

        #GET USER CREDITS
        user_credits = user.get_credit()

        #GET USER COMPLAINTS
        num_of_complaints = db.session.query(User_Complaints).filter_by(complained_id = userid).count()

        #CALCULATE CREDIT AFTER SALE
        temp_credit = user.credits  - ((int(request.form['saleDuration'])) * 5) - ((int(request.form['saleDuration'])) * num_of_complaints)

        #UPDATE USER CREDITS
        if (temp_credit < 0):
            return render_template('no_credit.html')



        user.credits = temp_credit



        file = form.data.get('bookImage')
        
        
        tempBool = 0
        b = Book()
        

        filename = ''.join(random.choice(string.ascii_letters+string.digits) for x in range(20))
        
        if (str(request.files['bookImage']) == "<FileStorage: u'' ('application/octet-stream')>"):    
            print "NO IMAGE"
            b.image_name = "noImage.jpg"
        else:
            #file = form.data.get('bookImage')
            file = request.files['bookImage']
            file.filename = filename+".jpg"
            if file and allowed_file(file.filename):
                #UPLOAD FILE
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                b.image_name = filename
            
        
    
        #PUSH DATA TO DB
        
        b.title = request.form['title']
        b.author = request.form['author']
        b.isbn = request.form['isbn']
        b.price = float(request.form['price'])
        b.saleDuration = int(request.form['saleDuration'])
        b.publisher = request.form['publisher']
        b.numOfPages = int(request.form['numOfPages'])
        b.lang = request.form['lang']
        b.condition = request.form['condition']
        b.genre = request.form['genre']
        b.bookType = request.form['bookType']
        b.edition = int(request.form['edition'])
        b.information = request.form['information']

        tempBool=0
        
        

        if (form.data.get('buyable') == 'True'):
            tempBool = 1;
        else:
            tempBool = 0;

        b.buyable = tempBool
        
        if (tempBool == 1):
            b.buyout_price = float(request.form['buynowPrice'])
        

        
        # changing current_bid to price
        #b.current_bid=float(0)
        b.current_bid = b.price

        b.biddable= 1
        
        b.starting_bid=float(request.form['price'])

        b.owner_id=int(userid)
        db.session.add(b)
        db.session.commit()

        return render_template('success.html')

    return render_template('sell.html', form=form)


@app.route('/success', methods=['POST'])
@login_required
def success():
    return render_template('success.html');

@app.route('/browse')
def browse():
    b = Book()
    query = b.query.order_by(b.owner_id).all()
    numOfRows = len(query)
    #print query[0]
    #print query
    return render_template('browse.html', obj=query)

@app.route('/browse/<book_id>', methods=['POST', 'GET'])
def browse_book(book_id):
    """test template to show one book so you can bid or buy
    pass in book.id as parameter to load book. """
    form = BidForm()
    form2 = PostForm()
    # add comment form for book
    
    try:
        user = User.query.filter_by(id = session['user_id']).first()
        is_guest = False
    except KeyError:
        # it errors here so user is guest. create a guest user to post with.
        is_guest = True
        guest = User.query.filter_by(username='guest', email = 'GUEST@GUEST.COM').first()
        if not guest:
            guest = User(
                    username = 'guest',
                    first_name = 'GUEST',
                    last_name = 'GUEST',
                    email = 'GUEST@GUEST.COM',
                    password = 'GUEST'
                    )
            db.session.add(guest)
            db.session.commit()
        else:
            session['user_id'] = guest.id

    book = Book.query.filter_by(id = book_id).first()
    if book is None:
        # temporary
        return 'book does not exist'
    else:
        if request.method == 'POST' and form.validate_on_submit() and form.bid_amount.data and is_guest == False:
            bid_amount = request.form['bid_amount']
            book.create_bid(session['user_id'], bid_amount)
            #msg = 'Sucessfully placed a bid for %s' % bid_amount
            #flash(msg)
        if request.method == 'POST' and form2.validate_on_submit() and form2.post.data:
            # have no idea why the other one doesnt work
            text = form2.post.data
            book.create_comment(session['user_id'], text)

        comments = Book_Comments.query.filter_by(book=book).order_by(desc(Book_Comments.timestamp)).all()
    
    if is_guest is True:
        # delete session created by guest user
        del session['user_id']
    return render_template('browse_book.html', book=book, form=form, book_id=book_id, form2=form2, comments=comments)




@app.route('/no_credit')
def show_page():
    return render_template('no_credit.html')

@app.route('/rate_book')
def rate_book():
    result=[]
    b=Book()
    isbn = request.args.get('isbn')
    query = b.query.filter_by(isbn = isbn).all()
    for u in query:
        book_dict=u.__dict__
    user_query = User.query.filter_by(id = int(book_dict['owner_id']))
    return render_template('rate_book.html', query = query, user_query = user_query, isbn =isbn)
 
@app.route('/rate', methods = ['POST'])
def submit_rating():
    b = Book()
    isbn = request.form['isbn_num']
    ratings = request.form['rated']
    query = b.query.filter_by(isbn = isbn).first()
    book_query = b.query.filter_by(isbn = isbn).all()
    for r in book_query:
        book_dict=r.__dict__

    num_of_ratings = int(book_dict['num_of_rating'])
    query.rating = ratings
    query.num_of_rating = num_of_ratings + 1
    db.session.commit()
    return render_template('rate_success.html')



@app.route('/complain')
def complain():
    b=Book()
    form = ComplainForm()
    isbn = request.args.get('isbn')
    query = b.query.filter_by(isbn = isbn).all()
    for u in query:
        book_dict = u.__dict__
    user_query = User.query.filter_by(id = int(book_dict['owner_id']))
    return render_template('complain.html', query = query, user_query = user_query, isbn =isbn, form = form)
    #return render_template('complain.html', query = query)

@app.route('/admin/make_superuser')
@login_required
# make registered user in to super user
def make_self_superuser():
    """simple function to make self super user"""
    user = User.query.filter_by(id = session['user_id']).first()
    user.superuser = True
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/get_admin_account')
def create_admin_account():
    u = User(
            username = 'admin',
            first_name = 'admin',
            last_name = 'admin',
            email = 'admin',
            password = 'admin'
            )
    u.superuser = True
    u.apr_by_admin = True
    db.session.add(u)
    db.session.commit()
    return render_template('home.html')





