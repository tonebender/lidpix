#!/usr/bin/env python

# This uses flask, flask-login, sqlite3 and WTForms

# flask-login:
# https://realpython.com/blog/python/using-flask-login-for-user-management-with-flask/
# https://gist.github.com/alanhamlett/11229056
# http://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works
# https://gist.github.com/bkdinoop/6698956

# SQLite3 tutorial:
# http://www.python-course.eu/sql_python.php
# http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html

# BCrypt:
# http://prettyprinted.com/using-bcrypt-in-python/

from flask import Flask, request, render_template, flash, redirect, \
url_for, abort, Blueprint, current_app, json
from wtforms import Form, StringField, PasswordField, BooleanField, validators
from flask_login import (LoginManager, current_user, login_required, \
login_user, logout_user, UserMixin, confirm_login, login_url, \
fresh_login_required)
import sqlite3, bcrypt


authz = Blueprint('authz', __name__)


# Initialize the flask-login manager
login_manager = LoginManager()
login_manager.login_view = "authz.login"
login_manager.login_message = "Please log in to access this page."
#login_manager.refresh_view = "reauth"

# This will be run when this blueprint is first registered to the app
@authz.record_once
def on_load(state):
    login_manager.init_app(state.app)


class LoginForm(Form):
    """The login form class, a subclass of Form, using WTForms."""
    username = StringField('Username', [validators.Required(), 
                           validators.Length(min=3)], render_kw={"placeholder": "username"})
    password = PasswordField('Password', [validators.Required(),
                             validators.InputRequired()], render_kw={"placeholder": "password"})
    remember = BooleanField('Remember me')


class UserDB(UserMixin):
    """The user class with login-related states and personal data"""
    def __init__(self, id, username, password, fullname, joined, groups,
                 active=1, confirmdelete=1, viewmode=10, theme='default'):
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname
        self.joined = joined
        self.groups = groups
        self.active = False if active == 0 else True
        self.confirmdelete = False if confirmdelete == 0 else True
        self.viewmode = viewmode
        self.theme = theme
        
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
            
    def get_as_dict(self):
        # Return settings in json style dict
        return {'id': self.id,
                'username': self.username,
                'fullname': self.fullname,
                'joined': self.joined,
                'groups': self.groups,
                'active': self.active,
                'confirmdelete': self.confirmdelete,
                'viewmode': self.viewmode,
                'theme': self.theme}
    

def user_has_access(gallery):
    """ Check if current logged in user has access to gallery
    
    gallery is a Gallery object (see folder.py) containing variables
    users_r, users_w, groups_r and groups_w """
    
    return False
    

@login_manager.user_loader
def load_user(username):
    """Find username i database and return it.
    
    username is a string to be searched for in the lidpix user db.
    Returns an instance of UserDB with found user data; None if user not found.
    """
    connection = sqlite3.connect(current_app.config['DATABASE'])
    c = connection.cursor()
    command = 'SELECT * FROM lidpixusers WHERE username =?'
    c.execute(command, (username,))
    row = c.fetchone()
    connection.close()
    try:
        user = UserDB(*row) # Where row contains id, username, password, etc.
        return user
    except:
        return None


#@login_manager.unauthorized_handler
#def handle_needs_login():
#    flash("You have to be logged in to access this page.")
#    return redirect(url_for('authz.login', next=request.endpoint))


@authz.route('/login', methods=['GET', 'POST'])
def login():
    """Log the user in.
    
    GET: Show login form.
    POST: Get user's username and password through the WTForms form, find user 
    in the sqlite3 db, check against password (bcrypted), then
    log in with flask-login!
    """
    if current_user.is_authenticated:
        flash('Already logged in')
        return redirect(request.args.get("next") or 
                        url_for("folder.folder_view"))
    myform = LoginForm(request.form)
    error = None
    if request.method == 'POST':
        if myform.validate():
            user = load_user(myform.username.data)
            if user:
                if user.password == bcrypt.hashpw(myform.password
                .data.encode('utf-8'), user.password):
                    if login_user(user, remember=myform.remember.data):
                        return redirect(request.args.get("next") or url_for("folder.folder_view"))
                    else:
                        flash('User found but login failed')
                else:
                    flash('Wrong password')
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
    return redirect(url_for('authz.login'))


@authz.route('/getusername')
def get_username():
    """Return username (json string) if logged in, otherwise 'None' """
    if current_user.is_authenticated:
        return '{"username":"' + current_user.get_id() + '"}'
    return 'None'


@authz.route('/get_user_settings')
def get_user_settings():
    """Get settings from logged in user object and return as json"""
    if current_user.is_authenticated:
        return json.dumps(current_user.get_as_dict())
    return 'None'


@authz.route('/set_user_settings')
def set_user_settings():
    """Save settings posted as keywords to logged in user"""
    return 'None'
