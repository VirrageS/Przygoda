from datetime import datetime

from flask.ext.login import UserMixin

from app import db
from app.users import constants as USER

class User(UserMixin, db.Model):
	"""Provides class for User"""

	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(128), nullable=False, unique=True)
	username = db.Column('username', db.String(128), unique=True, index=True)
	password = db.Column('password', db.String(255))
	email = db.Column('email', db.String(64), unique=True, index=True)
	registered_on = db.Column('registered_on', db.DateTime, nullable=False)
	confirmed = db.Column(db.Boolean, nullable=False, default=False)
	confirmed_on = db.Column(db.DateTime, nullable=True)
	role = db.Column('role', db.SmallInteger, nullable=False, default=USER.USER)
	paid = db.Column('paid', db.Boolean, nullable=False, default=False)


	def __init__(self, username, password, email, social_id=None, confirmed=False, confirmed_on=None, paid=False):
		if social_id is None:
			social_id = "facebook$" + username

		self.social_id = social_id
		self.username = username
		self.password = password
		self.email = email
		self.registered_on = datetime.now()
		self.confirmed = confirmed
		self.confirmed_on = confirmed_on
		self.paid = paid

	def is_authenticated(self):
		return True

	def is_active(self):
		# TODO: change to email confirmed or not
		return True #self.confirmed

	def is_anonymous(self):
		return False

	def get_role(self):
		return USER.ROLE[self.role]

	def __repr__(self):
		return '<User %r>' % (self.username)
