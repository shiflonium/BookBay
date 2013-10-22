from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from models import User
from forms import SignUpForm, LoginForm

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
        


@app.route('/', methods = ['GET', 'POST'])
@app.route('/home', methods = ['GET', 'POST'])
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
        flash("logged in sucessfully :)")
        return redirect(request.args.get('next') or url_for('profile'))
        #return redirect(url_for('profile'))
    else:
        flash("incorrect password")
        return render_template('login.html',form=form)
    return render_template("login.html",form=form)

@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    return 'this is the profile page, if you can see this, you are logged in'

@app.route('/signout')
@login_required
def logout():
    logout_user()
    # delete session created during login
    #del session['email']
    return redirect(url_for('home'))

