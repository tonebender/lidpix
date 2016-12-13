#!/usr/bin/env python

# This uses flask, flask-login, sqlite3 and WTForms

# flask-login:
# https://realpython.com/blog/python/using-flask-login-for-user-management-with-flask/
# https://gist.github.com/alanhamlett/11229056
# http://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works
# https://gist.github.com/bkdinoop/6698956

# SQL3 tutorial:
# http://www.python-course.eu/sql_python.php
# http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html

# BCrypt:
# http://prettyprinted.com/using-bcrypt-in-python/

from flask import Flask, request, render_template, flash, redirect, \
url_for, abort
from wtforms import Form, StringField, PasswordField, BooleanField, validators
from flask_login import (LoginManager, current_user, login_required, \
login_user, logout_user, UserMixin, confirm_login, login_url, \
fresh_login_required)
import sqlite3


class LoginForm(Form):
    """The login form class, using WTForms."""
    username = StringField('Username', [validators.Required(), 
                           validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Required(),
                             validators.InputRequired()])
    remember = BooleanField('Remember me')


class UserDB(UserMixin):
    """The user class with login-related states and personal data"""
    def __init__(self, id, username, password, fname, lname, joined, 
                 active=True):
        self.id = id
        self.username = username
        self.password = password
        self.fname = fname
        self.lname = lname
        self.joined = joined
        self.active = active
        
    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active
    
    def is_authenticated(self):
        return True
    
    def get_id(self):
        try:
            return (self.username)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')
    #def get_id(self):
    #   return self.email


