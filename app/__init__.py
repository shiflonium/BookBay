import os
from config import basedir
from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

UPLOAD_FOLDER = os.getcwd() + '/userImages'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# get config settings from config.py
app.config.from_object('config')

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

# SQL Alchemy
db = SQLAlchemy(app)

from app import views, models
