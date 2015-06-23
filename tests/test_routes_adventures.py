import os
import unittest

from datetime import datetime
from config import base_dir
from werkzeug import check_password_hash, generate_password_hash

from flask import Flask, render_template, g
from flask.ext.testing import TestCase

from flask.ext.login import login_user, logout_user, login_required, LoginManager, current_user

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES

class RoutesTestCase(TestCase, unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'test.db')
		self.app = app.test_client()

		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def create_app(self):
		app = Flask(__name__)
		app.config['TESTING'] = True

		# Default port is 5000
		app.config['LIVESERVER_PORT'] = 8943
		return app

	def login(self, username, password):
	    return self.app.post('/users/login/', data=dict(
	        username=username,
	        password=password
	    ), follow_redirects=True)

	def logout(self):
	    return self.app.get('/users/logout/', follow_redirects=True)

	def test_adventures_new_route_requires_login(self):
		"""Ensure adventures new route requires a logged in user"""

		response = self.app.get('/adventures/new', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_adventures_show_route_big_number(self):
		"""Ensure that adventures_id is not to big"""

		response = self.app.get('/adventures/320392480213849032841024803284103248712', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_show_route_no_adventure(self):
		"""Ensure that show adventure require existing adventure"""

		response = self.app.get('/adventures/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_show_route_no_creator(self):
		"""Ensure that show adventure require existing creator"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		response = self.app.get('/adventures/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_show_route(self):
		"""Ensure that show adventure redirect us to the right place"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.app.get('/adventures/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('adventures/show.html')

	def test_adventures_join_requires_login(self):
		"""Ensure that join adventure requires login"""

		response = self.app.get('/adventures/join/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_adventures_join_big_number(self):
		"""Ensure that join adventure requires small adventure_id"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/3458304958390433485734895734085734', follow_redirects=True)

		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_join_adventure_no_adventure(self):
		"""Ensure that join adventure require existing adventure"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/1', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_join_adventure_join(self):
		"""Ensure that join adventure create adventure participant"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/1', follow_redirects=True)

		# check if user has been added to adventure
		participant = AdventureParticipant.query.filter_by(adventure_id=1, user_id=1).first()
		self.assertTrue(participant is not None)

		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_adventures_join_adventure_joined(self):
		"""Ensure that join adventure does not allow to join again"""

		# add adventure to database
		a = Adventure(creator_id=1, date=datetime.utcnow(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
		db.session.add(a)
		db.session.commit()

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		# login user to system
		self.login(username='john', password='a')

		response = self.app.get('/adventures/join/1', follow_redirects=True)

		# check if user has been added to adventure
		participant = AdventureParticipant.query.filter_by(adventure_id=1, user_id=1).first()
		self.assertTrue(participant is not None)

		response = self.app.get('/adventures/join/1', follow_redirects=True)

		participants = AdventureParticipant.query.filter_by(adventure_id=1, user_id=1).all()
		self.assertTrue(participants is not None)
		self.assertTrue(len(participants) == 1)
