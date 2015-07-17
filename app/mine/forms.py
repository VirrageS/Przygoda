from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField
from wtforms.validators import Required

class ReportForm(Form):
	subject = TextField(u'Subject', [Required()])
	message = TextAreaField(u'Message', [Required()])
