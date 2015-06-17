import os
import unittest

from datetime import datetime
from config import base_dir
from werkzeug import check_password_hash, generate_password_hash
from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, Coordinate, AdventureParticipant

class DatabaseTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_add_adventure_to_database(self):
		a = Adventure(user_id=2, date=datetime.utcnow(), info='Some info today', joined=10)
		db.session.add(a)
		db.session.commit()
		a = Adventure.query.filter_by(user_id=2).first()
		assert a.info == 'Some info today'
		assert a.joined == 10

		a = Adventure(user_id=2, date=datetime.utcnow(), info='Some info today', joined=10)
		db.session.add(a)
		db.session.commit()
		b = Adventure.query.filter_by(user_id=2).all()
		assert len(b) == 2

	def test_add_user_to_database(self):
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()
		u = User.query.filter_by(username='john').first()
		assert u.id == 1
		assert u.username == 'john'
		assert check_password_hash(u.password, 'a')
		assert u.email == 'john@example.com'

		u = User(username='johner', password=generate_password_hash('a'), email='susan@examplee.com')
		db.session.add(u)
		db.session.commit()
		u = User.query.filter_by(username='johner').first()
		assert u.id == 2
		assert u.username != 'john'
		assert u.username == 'johner'

	def test_add_coordinate_to_database(self):
		c = Coordinate(adventure_id=1, latitude=52.229937, longitude=21.011380)
		db.session.add(c)
		db.session.commit()

		c = Coordinate.query.filter_by(adventure_id=1).first()
		assert c.latitude == 52.229937
		assert c.longitude == 21.011380
