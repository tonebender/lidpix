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
url_for
from wtforms import Form, StringField, PasswordField, validators
from flask_login import (LoginManager, current_user, login_required, \
login_user, logout_user, UserMixin, confirm_login, fresh_login_required, \
login_url)
import sqlite3

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    SECRET_KEY='Gabba gabba hey'
)

# WTForms stuff

class LoginForm(Form):
	username = StringField('Username', [validators.Required(), validators.Length(min=4, max=25)])
	password = PasswordField('Password', [validators.Required(), validators.InputRequired()])
	

# flask-login stuff

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

# Simple user class for simple test login w/o password
class User(UserMixin):
	def __init__(self, name, id, active=True):
		self.name = name
		self.id = id
		self.active = active
		
	def is_active(self):
		return self.active
	
	def is_authenticated(self):
		return True

# Database-based user
class UserDB(UserMixin):
	def __init__(self, id, username, password, fname, lname, joined, active=True):
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
		
	#def get_id(self):
	#	return self.email

USERS = {
    1: User(u"Notch", 1),
    2: User(u"Steve", 2),
    3: User(u"Creeper", 3, False),
}
USER_NAMES = dict((u.name, u) for u in USERS.itervalues())
	
@login_manager.user_loader
def load_user(user_id):
	return USERS.get(int(user_id))

login_manager.init_app(app)


# Database stuff

def create_example_user_db():
	
	connection = sqlite3.connect('users_example.db')
	cursor = connection.cursor()
	
	# Delete existing
	cursor.execute("""DROP TABLE IF EXISTS flaskusers;""")
	
	sql_command = """
	CREATE TABLE flaskusers (
	user_nr INTEGER PRIMARY KEY,
	username VARCHAR(30),
	password BINARY(60),
	fname VARCHAR(30),
	lname VARCHAR(30),
	joining DATE,
	active BOOLEAN DEFAULT TRUE);"""
	
	cursor.execute(sql_command)
	
	flaskusers = [('steve', 'Steve', 'Jobs'),
	('woz', 'Steve', 'Wozniak'), ('bob', 'Robert', 'Noyce')]
	
	for p in flaskusers:
		format_str = """
		INSERT INTO flaskusers (user_nr, username, fname, lname)
		VALUES (NULL, "{username}", "{first}", "{last}");"""
		sql_command = format_str.format(username=p[0], first=p[1], \
		last=p[2])
		cursor.execute(sql_command)
	
	connection.commit()
	connection.close()
	
	return True
		

def get_username_in_db(username):
	"""Find username i database and return it, or None if not found."""
	connection = sqlite3.connect('users_example.db')
	c = connection.cursor()
		command = 'SELECT * FROM flaskusers WHERE username =?'
	c.execute(command, (username,))
	row = c.fetchone()
	connection.close()
	return row
	
		
if create_example_user_db():
	print "Created database with three example users ..."
	
woz = get_username_in_db('bob')
print "woz is:", woz
if woz:
	wozniak = UserDB(*woz)
	print wozniak


# This login() function uses the simple USER_NAMES dictionary
# (defined above) and no passwords to test flask-login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		flash('Already logged in')
		return redirect(url_for('index'))
	myform = LoginForm(request.form)
	error = None
	if request.method == 'POST':
		if myform.validate():
			if myform.username.data in USER_NAMES:
				if login_user(USER_NAMES[myform.username.data]):
					flash('Logged in!')
					return redirect(request.args.get("next") or url_for("index"))
				else:
					flash('User found but login failed')
			else:
				flash('User not found in database')
		else:
			flash('Form input did not validate')
	return render_template('loginform.html', form=myform, error=error)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash("Logged out")
	return redirect(url_for('login'))
		

@app.route('/index')
@app.route('/')
def index():
	if current_user.is_authenticated:
		return render_template('index.html')
	return redirect(login_url('login', url_for('index')))

