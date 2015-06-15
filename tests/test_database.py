import os
import unittest

from datetime import datetime
from config import basedir
from app import app, db
from app.users.models import User
from app.adventures.models import Adventure

class DatabaseTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_add_adventure_to_database(self):
		a = Adventure(user='john', date=datetime.utcnow(), info='Some info today', joined=10)
		db.session.add(a)
		db.session.commit()
		a = Adventure.query.filter_by(user='john').first()
		assert a.info == 'Some info today'
		assert a.joined == 10

		a = Adventure(user='john', date=datetime.utcnow(), info='Some info today', joined=10)
		db.session.add(a)
		db.session.commit()
		b = Adventure.query.filter_by(user='john').all()
		assert len(b) == 2

	def test_add_user_to_database(self):
		u = User(username='john', password='a', email='john@example.com')
		db.session.add(u)
		db.session.commit()
		u = User.query.filter_by(username='john').first()
		assert u.username == 'john'
		assert u.password == 'a'
		assert u.email == 'john@example.com'

		u = User(username='johner', password='a', email='susan@examplee.com')
		db.session.add(u)
		db.session.commit()
		u = User.query.filter_by(username='johner').first()
		assert u.username != 'john'
		assert u.username == 'johner'
