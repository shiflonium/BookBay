# -*- coding: utf8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


SECRET_KEY = 'super secret key'
CSRF_ENABLED = True

#
SQLALCHEMY_DATABASE_URI = 'mysql://softeng:softeng@localhost/softeng'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
