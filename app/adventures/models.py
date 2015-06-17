from datetime import datetime
from app import db
from app.users.models import User

class Adventure(db.Model):
	__tablename__ = 'adventures'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	date = db.Column('date', db.DateTime)
	info = db.Column('info', db.String)
	joined = db.Column('joined', db.Integer)

	def __init__(self, user_id, date, info, joined=1):
		self.user_id = user_id
		self.date = date
		self.info = info
		self.joined = joined
