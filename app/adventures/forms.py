from flask.ext.wtf import Form
from wtforms import DateField, TextAreaField, HiddenField, SelectField
from wtforms.validators import Required

from app.adventures import constants as ADVENTURES

#from wtforms_components import DateRange
#from datetime import datetime, date

class NewForm(Form):
	#validators=[DateRange(min=datetime.date().utcnow())]
	date = DateField(u'Data', format='%d.%m.%Y')
	mode = SelectField(u'Mode', choices=[(str(value), name) for value, name in ADVENTURES.MODES.items()])
	info = TextAreaField(u'Info', [Required()])

class EditForm(NewForm):
	id = HiddenField()
