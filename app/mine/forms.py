from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import Required, Email, Optional

class ReportForm(Form):
    email = StringField(u'Email', [Email(), Optional()])
    subject = StringField(u'Subject', [Optional()])
    message = TextAreaField(u'Message', [Required()])
