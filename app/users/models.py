from datetime import datetime
from app import db
from app.users import constants as USER
from flask.ext.login import UserMixin

class User(UserMixin, db.Model):
	"""Provides class for User"""

	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(128), nullable=False, unique=True)
	username = db.Column('username', db.String(120), unique=True, index=True)
	password = db.Column('password', db.String(255))
	email = db.Column('email', db.String(50), unique=True, index=True)
	registered_on = db.Column('registered_on', db.DateTime)
	# confirm
	confirmed = db.Column(db.Boolean, nullable=False, default=False)
	confirmed_on = db.Column(db.DateTime, nullable=True)
	# extra
	role = db.Column('role', db.SmallInteger, default=USER.USER)
	paid = db.Column(db.Boolean, nullable=False, default=False)


	def __init__(self, username, password, email, confirmed=False, social_id=None, paid=False, confirmed_on=None):
		if social_id is None:
			social_id = username

		self.social_id = social_id
		self.username = username
		self.password = password
		self.email = email
		self.registered_on = datetime.utcnow()
		self.confirmed = confirmed
		self.confirmed_on = confirmed_on
		self.paid = paid

	def is_authenticated(self):
		return True

	def is_active(self):
		# todo: change to email confirmed or not
		return True #self.confirmed

	def is_anonymous(self):
		return False

	def get_role(self):
		return USER.ROLE[self.role]

	def get_id(self):
		try:
			return unicode(self.id) # python 2
		except NameError:
			return str(self.id) # python 3

	def __repr__(self):
		return '<User %r>' % (self.username)
