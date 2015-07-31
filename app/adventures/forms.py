# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import DateTimeField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import Required

from app.adventures import constants as ADVENTURES

# TODO: add HiddenField for markers on map

#from wtforms_components import DateRange
from datetime import datetime

class NewForm(Form):
	#validators=[DateRange(min=datetime.date().utcnow())]
	date = DateTimeField(u'Date', format='%d.%m.%Y %H:%M')
	mode = SelectField(
		u'Mode',
		choices=[(str(value), name) for value, name in ADVENTURES.MODES.items()]
	)
	info = TextAreaField(u'Info', [Required()])

	def validate(self):
		if not Form.validate(self):
			return False

		# check if date is 'up-to-date'
		input_date = datetime.strptime(str(self.date.data), '%Y-%m-%d %H:%M:%S')
		if input_date < datetime.now():
			self.date.errors.append(gettext(u'Date must be older than now'))
			return False

		return True

class EditForm(NewForm):
	pass
	# id = HiddenField()

class SearchForm(Form):
	modes = SelectMultipleField(
		u'Modes',
		choices=[(str(value), name) for value, name in ADVENTURES.MODES.items()]
	)

	def validate(self):
		if not Form.validate(self):
			return False

		if (self.modes.data is None) or (len(self.modes.data) <= 0):
			self.modes.errors.append(gettext(u'Invalid Adventure mode'))
			return False

		return True
