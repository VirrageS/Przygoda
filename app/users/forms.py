from flask.ext.wtf import Form
from wtforms import BooleanField, StringField, PasswordField, validators
from wtforms.validators import Required, EqualTo, Email, Optional

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
	username = StringField('Username', [validators.Length(min=4, max=25)])
	password = PasswordField('Password', [Required()])
	remember_me = BooleanField('Remember me', [])

class RegisterForm(Form):
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email Address', [Email(), validators.Length(min=6, max=35)])
	password = PasswordField('Password', [Required()])
	confirm = PasswordField('Repeat Password', [Required(), EqualTo('password', message='Passwords must match')])

class AccountForm(Form):
	username = StringField('Username', [Optional(), validators.Length(min=4, max=25)])
	email = StringField('Email Address', [Email(), validators.Length(min=6, max=35)])
	password = PasswordField('Password', [Optional()])
	confirm = PasswordField('Repeat Password', [Optional(), EqualTo('password', message='Passwords must match')])
	old_password = PasswordField('Old Password', [RequiredIf('password')])
