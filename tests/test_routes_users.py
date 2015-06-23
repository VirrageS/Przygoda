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

class RoutesAdventuresTestCase(TestCase, unittest.TestCase):
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

	def test_users_login_wrong_username(self):
		"""Ensure users login does not accept wrong username"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='johne', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_users_login_wrong_password(self):
		"""Ensure users login does not accept wrong password"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='john', password='ab')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_users_login_login(self):
		"""Ensure users login actually login the user"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='john', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_users_login_no_login_again(self):
		"""Ensure users login does not allow to login again"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='john', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

		response = self.login(username='john', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

	def test_users_logout_requires_login(self):
		"""Ensure users logout requires login"""

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_users_logout_logout(self):
		"""Ensure users logout actually logout the user"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		self.login(username='john', password='a')

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('index.html')

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')
