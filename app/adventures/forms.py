from flask.ext.wtf import Form, RecaptchaField
from wtforms import BooleanField, TextField, DateField, TextAreaField, validators
from wtforms.validators import Required, EqualTo, Email
from wtforms_components import DateRange
from datetime import datetime, date

class NewForm(Form):
	#validators=[DateRange(min=datetime.date().utcnow())]
	date = DateField('Data', format='%d.%m.%Y')
	info = TextAreaField('Password', [Required()])

class RegisterForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=25)])
	email = TextField('Email Address', [validators.Length(min=6, max=35)])
