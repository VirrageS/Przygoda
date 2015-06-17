from flask.ext.wtf import Form, RecaptchaField
from wtforms import BooleanField, TextField, DateField, TextAreaField, validators
from wtforms.validators import Required, EqualTo, Email

class NewForm(Form):
	date = DateField('Data', [Required()], format='%d.%m.%Y')
	info = TextAreaField('Password', [Required()])

class RegisterForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=25)])
	email = TextField('Email Address', [validators.Length(min=6, max=35)])
