from datetime import datetime

from sqlalchemy import create_engine
from flask import Flask, session, request, flash, url_for, redirect, render_template, abort, g
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauth import OAuth
from flask.ext.googlemaps import GoogleMaps

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '188477911223606'
FACEBOOK_APP_SECRET = '621413ddea2bcc5b2e83d42fc40495de'

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

# Facebook auth
oauth = OAuth()

facebook = oauth.remote_app('facebook',
	base_url='https://graph.facebook.com/',
	request_token_url=None,
	access_token_url='/oauth/access_token',
	authorize_url='https://www.facebook.com/dialog/oauth',
	consumer_key=FACEBOOK_APP_ID,
	consumer_secret=FACEBOOK_APP_SECRET,
	request_token_params={'scope': 'email'}
)


# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

# Database setup
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = "users"
	id = db.Column('user_id', db.Integer, primary_key=True)
	username = db.Column('username', db.String(20), unique=True, index=True)
	password = db.Column('password', db.String(10))
	email = db.Column('email', db.String(50), unique=True, index=True)
	registered_on = db.Column('registered_on' , db.DateTime)

	def __init__(self, username, password, email):
		self.username = username
		self.password = password
		self.email = email
		self.registered_on = datetime.utcnow()

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)  # python 2
		except NameError:
			return str(self.id)  # python 3

	def __repr__(self):
		return '<User %r>' % (self.username)

class Adventure(db.Model):
	__tablename__ = 'adventure'
	id = db.Column('adventure_id', db.Integer, primary_key=True)
	user = db.Column('user', db.String(60))
	date = db.Column('date', db.DateTime)
	info = db.Column('info', db.String)
	users_joined = db.Column('users_joined', db.Integer, index=True)

	def __init__(self, info, users_joined):
		self.user = current_user.username
		self.date = datetime.utcnow()
		self.info = info
		self.users_joined = users_joined

# Main path - layout
@app.route("/")
def index():
	return render_template('index.html',
		adventures = Adventure.query.order_by(Adventure.date.desc()).all()
	)

# New trip
@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
	if request.method == 'POST':
		if not request.form['info']:
			flash('Info is required', 'error')
		else:
			adventure = Adventure(request.form['info'], 1)
			db.session.add(adventure)
			db.session.commit()
			flash(u'Adventure item was successfully created')
			return redirect(url_for('index'))

	return render_template('new.html')

@app.route('/adventures')
@login_required
def adventures():
	return render_template('adventure.html')

# Register
@app.route('/register' , methods=['GET','POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html')
	user = User(request.form['username'] , request.form['password'], request.form['email'])
	db.session.add(user)
	db.session.commit()
	flash('User successfully registered')
	return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')

	username = request.form['username']
	password = request.form['password']
	remember_me = False
	if 'remember_me' in request.form:
		remember_me = True
	registered_user = User.query.filter_by(username=username,password=password).first()
	if registered_user is None:
		flash('Username or Password is invalid' , 'error')
		return redirect(url_for('login'))
	login_user(registered_user, remember = remember_me)
	flash('Logged in successfully')
	return redirect(request.args.get('next') or url_for('index'))

# Logout
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.before_request
def before_request():
	g.user = current_user

if __name__ == "__main__":
	db.create_all()
	GoogleMaps(app)
	app.run()
