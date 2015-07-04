from flask.ext.wtf import Form
from wtforms import BooleanField, StringField, PasswordField
from wtforms.validators import Required, EqualTo, Email, Optional, Length

from werkzeug import check_password_hash, generate_password_hash
from flask.ext.login import current_user
from app.users.models import User
import re

def validate_username(username):
	return username == re.sub('[^a-zA-Z0-9_\.]', '', username)

class RequiredIf(Required):
	# a validator which makes a field required if
	# another field is set and has a truthy value

	def __init__(self, other_field_name, *args, **kwargs):
		self.other_field_name = other_field_name
		super(RequiredIf, self).__init__(*args, **kwargs)

	def __call__(self, form, field):
		other_field = form._fields.get(self.other_field_name)
		if other_field is None:
			raise Exception('no field named "%s" in form' % self.other_field_name)
		if bool(other_field.data):
			super(RequiredIf, self).__call__(form, field)

class LoginForm(Form):
	username = StringField('Username', [Length(min=4, max=25)])
	password = PasswordField('Password', [Required()])
	remember_me = BooleanField('Remember me', [])

	# def validate(self):
	# 	if not Form.validate(self):
	# 		return False
	#
	# 	# check username and password
	# 	user = User.query.filter_by(username=self.username.data).first()
	# 	if (user is None) or (not check_password_hash(user.password, self.password.data)):
	# 		self.username.errors.append(u'Nie prawidłowe hasło lub nazwa użytkownika')
	# 		return False

class RegisterForm(Form):
	username = StringField('Username', [Length(min=4, max=25)])
	email = StringField('Email Address', [Email(), Length(min=6, max=35)])
	password = PasswordField('Password', [Required()])
	confirm = PasswordField('Repeat Password', [Required(), EqualTo('password', message='Passwords must match')])

	def validate(self):
		if not Form.validate(self):
			return False

		# check if username has valid characters
		if not validate_username(self.username.data):
			self.username.errors.append('Username contains illegal characters')
			return False

		# check username
		user = User.query.filter_by(username=self.username.data).first()
		if user is not None:
			self.username.errors.append('This username is already in use. Please choose another one.')
			return False

		# email check
		user = User.query.filter_by(email=self.email.data.lower()).first()
		if user is not None:
			self.email.errors.append('This email is already in use.')
			return False

		return True

class AccountForm(Form):
	username = StringField('Username', [Length(min=4, max=25)])
	email = StringField('Email Address', [Email(), Length(min=6, max=35)])
	password = PasswordField('Password', [Optional()])
	confirm = PasswordField('Repeat Password', [Optional(), EqualTo('password', message='Passwords must match')])
	old_password = PasswordField('Old Password', [RequiredIf('password')])

	def validate(self):
		if not Form.validate(self):
			return False

		# check if username has valid characters
		if not validate_username(self.username.data):
			self.username.errors.append('Username contains illegal characters')
			return False

		# check username
		user = User.query.filter_by(username=self.username.data).first()
		if (user is not None) and (user.id != current_user.id):
			self.username.errors.append('This username is already in use. Please choose another one.')
			return False

		# email check
		user = User.query.filter_by(email=self.email.data.lower()).first()
		if (user is not None) and (user.id != current_user.id):
			self.email.errors.append('This email is already in use.')
			return False

		# check old password
		if ((self.old_password.data is not None) and
			(self.old_password.data is not '') and
			(not check_password_hash(current_user.password, self.old_password.data))):
			self.old_password.errors.append('Old password is not correct')
			return False

		self.password.data = generate_password_hash(self.password.data)
		return True
