from flask.ext.wtf import Form
from wtforms import DateTimeField, TextAreaField, HiddenField, SelectField, SelectMultipleField, widgets
from wtforms.validators import Required

from app.adventures import constants as ADVENTURES

#from wtforms_components import DateRange
#from datetime import datetime, date

class NewForm(Form):
	#validators=[DateRange(min=datetime.date().utcnow())]
	date = DateTimeField(u'Date', format='%d.%m.%Y %H:%M')
	mode = SelectField(
		u'Mode',
		choices=[(str(value), name) for value, name in ADVENTURES.MODES.items()]
	)
	info = TextAreaField(u'Info', [Required()])

class EditForm(NewForm):
	pass
	# id = HiddenField()

class SearchForm(Form):
	modes = SelectMultipleField(
		u'Modes',
		choices=[(str(value), name) for value, name in ADVENTURES.MODES.items()],
		option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
	)
