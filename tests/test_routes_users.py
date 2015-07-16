# -*- coding: utf-8 -*-

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

class RoutesUsersTestCase(TestCase, unittest.TestCase):
	def setUp(self):
		app.config.from_object('config.TestingConfig')
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

	def test_users_login_route_wrong_username(self):
		"""Ensure users login does not accept wrong username"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='johne', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_users_login_route_wrong_password(self):
		"""Ensure users login does not accept wrong password"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='john', password='ab')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_users_login_route_login(self):
		"""Ensure users login actually login the user"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='john', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('all.html')

	def test_users_login_route_no_login_again(self):
		"""Ensure users login does not allow to login again"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(username='john', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('all.html')

		response = self.login(username='john', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('all.html')

	def test_users_logout_route_requires_login(self):
		"""Ensure users logout requires login"""

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_users_logout_route_logout(self):
		"""Ensure users logout actually logout the user"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		self.login(username='john', password='a')

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('landing.html')

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	def test_users_register_route_no_register_when_logged(self):
		"""Ensure users register does not allow to register when user is logged in"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		self.login(username='john', password='a')

		response = self.app.get('/users/register', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('all.html')

	def test_users_register_route_too_short_username(self):
		"""Ensure users register does not allow to register when username is too short"""

		response = self.app.post('/users/register/', data=dict(
			username='a',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')

	def test_users_register_route_wrong_email(self):
		"""Ensure users register does not allow to register with wrong email address"""

		response = self.app.post('/users/register/', data=dict(
			username='tomek',
			email='tomektomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')

	def test_users_register_route_wrong_confirm_password(self):
		"""Ensure users register does not allow to register with wrong confirmed password"""

		response = self.app.post('/users/register/', data=dict(
			username='tomek',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')

	def test_users_register_route_user_exists_with_username(self):
		"""Ensure users register does not allow to register when someone exists with username"""

		u = User(username='tomek', password=generate_password_hash('a'), email='tomeked@tomek.com')
		db.session.add(u)
		db.session.commit()

		response = self.app.post('/users/register/', data=dict(
			username='tomek',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')

	def test_users_register_route_user_exists_with_email(self):
		"""Ensure users register does not allow to register when someone exists with email"""

		u = User(username='tomeczek', password=generate_password_hash('a'), email='tomek@tomek.com')
		db.session.add(u)
		db.session.commit()

		response = self.app.post('/users/register/', data=dict(
			username='tomek',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')

	def test_users_register_route_register(self):
		"""Ensure users register actually create the user"""

		response = self.app.post('/users/register/', data=dict(
			username='tomeker',
			email='tomeker@tomekads.com',
			password='aaaaaa',
			confirm='aaaaaa'
		), follow_redirects=True)

		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

		u = User.query.filter_by(username='tomeker').first()
		self.assertTrue(u is not None)
		self.assertTrue(u.email == 'tomeker@tomekads.com')
		self.assertTrue(check_password_hash(u.password, 'aaaaaa'))
