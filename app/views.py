from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from models import User, Book, Transaction, Bid
from forms import SignUpForm, LoginForm, ChangePassword, ChangePersonalDetails, SearchForm, sellForm, BidForm
from werkzeug import generate_password_hash, check_password_hash, secure_filename
from datetime import datetime
from sqlalchemy import desc
import os
import random
import string


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
        # put user_id in session for later use
        session['user_id'] = user.id
        db.session.add(user)
        db.session.commit()
        
        flash("logged in sucessfully :)")
        return redirect(request.args.get('next') or url_for('profile'))
        #return redirect(url_for('profile'))
    else:
        flash("incorrect password")
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

    #RIGHT NOW SET TO FALSE FOR EASIER DEBUGGING
    if user.superuser == False:
        trans = Transaction.query.all()
        return render_template('transaction_history.html', trans=trans)
    else:
        return redirect(url_for('home'))


@app.route('/admin/bid_history', methods=['GET', 'POST'])
@login_required
def bid_history():
    user = User.query.filter_by(id = session['user_id']).first()
    
    # debug
    if user.superuser == False:
        bids = Bid.query.order_by(desc(Bid.timestamp)).all()
        return render_template('bid_history.html', bids=bids)
    else:
        return redirect(url_for('home'))


@app.route('/admin/user_list', methods=['GET', 'POST'])
@login_required
def get_all_users():
    user = User.query.filter_by(id = session['user_id']).first()

    # setting to false for now
    if user.superuser == False:
        user_data = User.query.all()
        return render_template('user_list.html',
                user_data = user_data
                )

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

        #UPDATE USER CREDITS
        if ((user.credits  - (int(request.form['saleDuration'])) * 5) < 0):
            return "NOT ENOUGH CREDIT"

        user.credits = user.credits  - (int(request.form['saleDuration'])) * 5



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
        

        

        b.current_bid=float(0)

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

    print query[0]



    print query



    return render_template('browse.html', obj=query)

@app.route('/browse/<book_id>', methods=['POST', 'GET'])
@login_required
def browse_book(book_id):
    """test template to show one book so you can bid or buy
    pass in book.id as parameter to load book. """
    form = BidForm()
    # add comment form for book

    book = Book.query.filter_by(id = book_id).first()
    if book is None:
        # temporary
        return 'book does not exist'
    else:
        if request.method == 'POST' and form.validate_on_submit():
            bid_amount = request.form['bid_amount']
            book.create_bid(session['user_id'], bid_amount)
            #if bid_amount < book.current_bid:
            #    print 'current_bid %s' % book.current_bid
            #    print 'bid amount: %s' % bid_amount
            #    return 'bid amount too low, current bid: %s ' % book.current_bid

    return render_template('browse_book.html', book=book, form=form, book_id=book_id)


@app.route('/view_profile/<user_id>', methods = ['GET', 'POST'])
def view_profile(user_id):
    #username_from_get = request.args.get()
    query = User.query.filter_by(id = user_id)
    return render_template('view_profile.html', user_id = user_id, query = query)



@app.route('/no_credit')
def show_page():
    return render_template('no_credit.html')
