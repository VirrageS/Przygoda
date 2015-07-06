from app import db
from app.adventures import constants as ADVENTURES

from datetime import datetime

class Adventure(db.Model):
	__tablename__ = 'adventures'
	id = db.Column(db.Integer, primary_key=True)
	creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	date = db.Column('date', db.DateTime)
	mode = db.Column('mode', db.SmallInteger)
	info = db.Column('info', db.String)
	views = db.Column('views', db.BigInteger)
	searched = db.Column('searched', db.BigInteger)

	def __init__(self, creator_id, date, mode, info):
		self.creator_id = creator_id
		self.date = date
		self.mode = mode
		self.info = info
		self.views = 0
		self.searched = 0

	def get_mode(self):
		return ADVENTURES.MODES[self.mode]

	def is_active(self):
		"""Checks if adventure is active"""
		return self.date >= datetime.now()

class Coordinate(db.Model):
	__tablename__ = 'coordinates'
	id = db.Column(db.Integer, primary_key=True)
	adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
	path_point = db.Column('path_point', db.Integer)
	latitude = db.Column('latitude', db.Float)
	longitude = db.Column('longitude', db.Float)

	def __init__(self, adventure_id, path_point, latitude, longitude):
		self.adventure_id = adventure_id
		self.path_point = path_point
		self.latitude = latitude
		self.longitude = longitude

class AdventureParticipant(db.Model):
	__tablename__ = 'adventure_participants'
	id = db.Column(db.Integer, primary_key=True)
	adventure_id = db.Column(db.Integer, db.ForeignKey('adventures.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def __init__(self, adventure_id, user_id):
		self.adventure_id = adventure_id
		self.user_id = user_id
