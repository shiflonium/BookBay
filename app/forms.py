from flask_wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SubmitField, PasswordField,SelectField, validators, ValidationError, FloatField
from app.models import User
from flask import flash
from wtforms.validators import NumberRange, Required
from wtforms.fields import IntegerField


class SignUpForm(Form):
    username = TextField('Username', validators=[validators.Required()])
    first_name = TextField('First name', validators=[validators.Required()])
    last_name = TextField('Last Name', validators=[validators.Required()])
    email = TextField('Email', validators=[validators.Required()])
    #password = PasswordField('Password', validators=[validators.Required()])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        '''custom validators method. this method is referenced everytime
        form.validate_on_submit() is called. when returned False, will
        prompt the client as error'''
        if not Form.validate(self):
            return False
        # check if email is taken and if password is correct
        email = User.query.filter_by(email = self.email.data.lower()).first()
        username = User.query.filter_by(username = self.username.data.lower()).first()
        if email:
            self.email.errors.append("That email is already taken")
        if username:
            self.username.errors.append("This username is already taken")
        else:
            return True

class LoginForm(Form):
    username = TextField('Username', validators=[validators.Required()])
    password = PasswordField('Password',validators=[validators.Required("Please enter a password.")])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(username = self.username.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.password.errors.append("invalid password")


class ChangePassword(Form):
    oldPassword = PasswordField('Old Password:', validators=[validators.Required()])
    newPassword = PasswordField('New Password:', validators=[validators.Required("Please enter a password")])
    newPassword2 = PasswordField('New Password:', validators=[validators.Required("Passwords does not match")])
    submit = SubmitField("Change Password")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        if user and user.check_password(self.oldPassword.data):
            if (self.newPassword == newPassword2):
                return True
        return False

class PostForm(Form):
    post = TextAreaField('post', validators = [validators.Required()])
    submit = SubmitField('post!')
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        
    def validate(self):
        return True

class SUForm(Form):
    message = TextAreaField('message', validators = [validators.Required()])
    status = IntegerField('status', validators=[validators.Required()])
    submit = SubmitField('submit')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True



class ChangePersonalDetails(Form):

    first_name = TextField('First Name:', validators=[validators.Required()])
    last_name = TextField('Last Name:', validators=[validators.Required()])
    updateDatails = SubmitField("Change Details")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)



class SearchForm(Form):
    search_field = TextField(u'Search:')
    search_type = SelectField(u'Type of Search', choices=[('books','Books'), ('users', 'People')])
    submit = SubmitField("Submit")



class sellForm(Form):

    def buy_now_validator(self,field):
        if (self.data.get('buyable') == True):
            if (self.data.get('buynowPrice') == ''):
                raise ValidationError('You must specify a price for the Buy Now option')
                return False
            if (self.data.get('buynowPrice') < 0):
                raise ValidationError('Illegal price')
                return False

        return True
        
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        # if (self.data.get('buyable') == True):
            # if self.data.get('buynowPrice') == '':
                # return False
        
        else:
            return True
    
    title = TextField('Title:', validators=[validators.Required(message = 'Required field')])
    author = TextField('Author', validators=[validators.Required(message = 'Required field')])
    isbn = TextField('ISBN', validators=[validators.Required(message = 'Required field'), validators.Length(min=10, max=13, message = "ISBN is not the right length")])
    price = IntegerField('Price:',[NumberRange(min = 0, max=None ,message = "Illegal price. Please enter a number"), Required(message = 'Required field')])
    saleDuration = IntegerField('Sale duration (days):', validators=[validators.Required(message = 'Required field'), validators.NumberRange(min=1, max=3, message= "The sale duration must be 1-3 days")])
    publisher = TextField('Publisher:', validators=[validators.Required(message = 'Required field')])
    numOfPages = IntegerField('No. of Pages:', validators=[validators.Required( message = 'Required field'), validators.NumberRange(min=0, max=None, message = "Illegal number of pages")])
    lang = TextField('Language:', validators=[validators.Required(message = 'Required field')])
    genre = TextField('Genre:', validators=[validators.Required(message = 'Required field')])
    edition = IntegerField('Edition:', validators=[validators.Required(message = 'Required field'), validators.NumberRange(min=0, max=None, message = 'Illegal edition number')])
    condition = SelectField('Condition', choices=[('new','New'),('used','Used')])
    bookType = SelectField('Type:', choices=[('paperBack','Paper back'),('hardCover','Hard Cover')])
    information = TextAreaField('Book Information', validators = [validators.Length(min=0, max=100, message="Please enter at most 100 characters")])
    submit = SubmitField("Post For Sale!")
    buyable = BooleanField("Enable Buy Now")
    buynowPrice = IntegerField("Buy Now Price:", validators = [buy_now_validator])



    

    

class BidForm(Form):

    bid_amount = FloatField('Amount bid:', validators=[validators.Required()])
    submit_bid = SubmitField('Submit Bid')
    submit_buy_now = SubmitField('BuyNow!!')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True


class ComplainForm(Form):
    message = TextAreaField('message', validators = [validators.Required()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True



