from app.metrics import constants as METRICS

from app.adventures.models import Adventure, AdventureParticipant
from app.users.models import User
from app.metrics.models import Metric

from datetime import datetime

import sys
from time import sleep
from apscheduler.scheduler import Scheduler

sched = Scheduler()
sched.start() # start the scheduler

def get_active_adventures():
	adventures = Adventure.query.all()
	adventures = list(filter(lambda a: a.is_active(), adventures))
	return len(adventures)

def get_inactive_adventures():
	adventures = Adventure.query.all()
	adventures = list(filter(lambda a: not a.is_active(), adventures))
	return len(adventures)

def get_all_adventures():
	adventures = Adventure.query.all()
	return len(adventures)

def get_all_users():
	users = User.query.all()
	return len(users)

def get_users_per_adventure():
	adventures = Adventure.query.all()

	if len(adventures) == 0:
		return 0

	all_participants = 0
	for adventure in adventures:
		ap = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
		all_participants += len(ap)

	return all_participants / len(adventures)

class Metrics(object):

	def __init__(self, db):
		self.db = db

	def update_all(self):
		m = Metric(type=METRICS.ADVENTURES_COUNT_ACTIVE, counter=get_active_adventures(), date=datetime.now())
		self.db.session.add(m)

		m = Metric(type=METRICS.ADVENTURES_COUNT_INACTIVE, counter=get_inactive_adventures(), date=datetime.now())
		self.db.session.add(m)

		m = Metric(type=METRICS.ADVENTURES_COUNT_ALL, counter=get_all_adventures(), date=datetime.now())
		self.db.session.add(m)

		m = Metric(type=METRICS.ADVENTURES_COUNT_ACTIVE, counter=get_all_users(), date=datetime.now())
		self.db.session.add(m)

		m = Metric(type=METRICS.USERS_PER_ADVENTURE, counter=get_users_per_adventure(), date=datetime.now())
		self.db.session.add(m)
		self.db.session.commit()

	def update_metrics(self, interval=3600*24):
		sched.add_interval_job(self.update_all, seconds=30, args=[])
