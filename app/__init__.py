import os
from config import basedir
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
# get config settings from config.py
app.config.from_object('config')

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

# SQL Alchemy
db = SQLAlchemy(app)

from app import views, models
