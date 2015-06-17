from datetime import datetime
from app import db

class Adventure(db.Model):
	__tablename__ = 'adventure'
	id = db.Column('adventure_id', db.BigInteger, autoincrement=True, primary_key=True)
	user_id = db.Column('id', db.Integer)
	date = db.Column('date', db.DateTime)
	info = db.Column('info', db.String)
	joined = db.Column('joined', db.Integer)

	def __init__(self, user_id, date, info, joined=1):
		self.user_id = user_id
		self.date = date
		self.info = info
		self.joined = joined
