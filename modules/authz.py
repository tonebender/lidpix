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
url_for, abort, Blueprint
from wtforms import Form, StringField, PasswordField, BooleanField, validators
from flask_login import (LoginManager, current_user, login_required, \
login_user, logout_user, UserMixin, confirm_login, login_url, \
fresh_login_required)
import sqlite3


authz = Blueprint('authz', __name__)

login_manager = LoginManager()

@authz.record_once
def on_load(state):
    login_manager.init_app(state.app)


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
    

@login_manager.user_loader
def load_user(username):
    """Find username i database and return it.
    
    username is a string to be searched for in the db.
    Returns an instance of UserDB with found user data; None if user not found.
    """
    connection = sqlite3.connect('users_example.db')
    c = connection.cursor()
    command = 'SELECT * FROM flaskusers WHERE username =?'
    c.execute(command, (username,))
    row = c.fetchone()
    connection.close()
    try:
        user = UserDB(*row)
        return user
    except:
        return None



#def load_user(user_id):
#    return USERS.get(int(user_id))  # <===========================


# This login() function uses the simple USER_NAMES dictionary
# (defined above) and no passwords to test flask-login
@authz.route('/login', methods=['GET', 'POST'])
def login():
    """Log the user in.
    
    Get user's username and password through the WTForms form, find user 
    in the sqlite3 db, check against password (bcrypted), then
    log in with flask-login!
    """
    if current_user.is_authenticated:
        flash('Already logged in')
        return redirect(url_for('gallery'))
    myform = LoginForm(request.form)
    error = None
    if request.method == 'POST':
        if myform.validate():
            user = load_user(myform.username.data)
            if user:
                if login_user(user, remember=myform.remember.data):
                    flash('Logged in!')
                    return redirect(url_for('gallery'))
                    #return redirect(request.args.get("next") or url_for("index"))
                else:
                    flash('User found but login failed')
            else:
                flash('User not found in database')
        else:
            flash('Form input did not validate')
    return render_template('loginform.html', form=myform, error=error)


@authz.route('/logout')
@login_required
def logout():
    """Log the user out and then go to the login form page."""
    logout_user()
    flash("Logged out")
    return redirect(url_for('login'))
