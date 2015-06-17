from flask.ext.wtf import Form, RecaptchaField
from wtforms import BooleanField, TextField, PasswordField, validators
from wtforms.validators import Required, EqualTo, Email

class LoginForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=25)])
	password = PasswordField('Password', [Required()])
	remember_me = BooleanField('Remember me', [])

class RegisterForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=25)])
	email = TextField('Email Address', [Email(), validators.Length(min=6, max=35)])
	password = PasswordField('Password', [Required()])
	confirm = PasswordField('Repeat Password', [Required(), EqualTo('password', message='Passwords must match')])
