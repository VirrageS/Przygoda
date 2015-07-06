from app import db
from app.metrics import constants as METRICS

from app.adventures.models import Adventure, AdventureParticipant
from app.users.models import User

from datetime import datetime

class Metric(db.Model):
	__tablename__ = 'metrics'
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column('type', db.SmallInteger)
	counter = db.Column('counter', db.BigInteger)
	date = db.Column('date', db.DateTime)

	def __init__(self, type, counter, date):
		self.type = type
		self.counter = counter
		self.date =  date
