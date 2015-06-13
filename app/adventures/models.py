from datetime import datetime
from app import db

class Adventure(db.Model):
	__tablename__ = 'adventure'
	id = db.Column('adventure_id', db.Integer, primary_key=True)
	user = db.Column('user', db.String(60))
	date = db.Column('date', db.DateTime)
	info = db.Column('info', db.String)
	joined = db.Column('joined', db.Integer)

	def __init__(self, user, date, info, joined=1):
		self.user = user
		self.date = date
		self.info = info
		self.joined = joined
