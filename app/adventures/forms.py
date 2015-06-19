from flask.ext.wtf import Form
from wtforms import TextField, DateField, TextAreaField, validators, HiddenField
from wtforms.validators import Required
#from wtforms_components import DateRange
#from datetime import datetime, date

class NewForm(Form):
	#validators=[DateRange(min=datetime.date().utcnow())]
	date = DateField('Data', format='%d.%m.%Y')
	info = TextAreaField('Info', [Required()])

class EditForm(NewForm):
	id = HiddenField()
