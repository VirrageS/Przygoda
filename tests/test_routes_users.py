# -*- coding: utf-8 -*-

import os
import unittest

from datetime import datetime
from config import base_dir
from werkzeug import check_password_hash, generate_password_hash

from flask import Flask, render_template, g
from flask_testing import TestCase

from flask_login import login_user, logout_user, login_required, LoginManager, current_user

from app import app, db, mail
from app.users.models import User
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES
from flask_mail import Mail

class RoutesUsersTestCase(TestCase, unittest.TestCase):
	def setUp(self):
		app.config.from_object('config.TestingConfig')
		mail = Mail(app)
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def create_app(self):
		app = Flask(__name__)

		# Default port is 5000
		app.config['LIVESERVER_PORT'] = 8943
		return app

	def login(self, email, password):
		return self.app.post('/users/login/', data=dict(
			email=email,
			password=password
		), follow_redirects=True)

	def logout(self):
		return self.app.get('/users/logout/', follow_redirects=True)

	def test_users_login_route_wrong_email(self):
		"""Ensure users login does not accept wrong email"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(email='johner@example.com', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')
		self.assertIn(b'Incorrect email or password', response.data)

	def test_users_login_route_wrong_password(self):
		"""Ensure users login does not accept wrong password"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(email='john@example.com', password='ab')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')
		self.assertIn(b'Incorrect email or password', response.data)

	def test_users_login_route_login(self):
		"""Ensure users login actually login the user"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(email='john@example.com', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('all.html')

	def test_users_login_route_no_login_again(self):
		"""Ensure users login does not allow to login again"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		response = self.login(email='john@example.com', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('all.html')

		response = self.login(email='john@example.com', password='a')
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('all.html')

	###
	### LOGOUT FORM
	###

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

		self.login(email='john@example.com', password='a')

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('landing.html')

		response = self.logout()
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')

	###
	### REGISTER FORM
	###

	def test_users_register_route_no_register_when_logged(self):
		"""Ensure users register does not allow to register when user is logged in"""

		# add user to database
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(u)
		db.session.commit()

		self.login(email='john@example.com', password='a')

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
		self.assertIn(b'Field must be between 4 and 25 characters long.', response.data)

	def test_users_register_route_too_long_username(self):
		"""Ensure users register does not allow to register when username is too long"""

		response = self.app.post('/users/register/', data=dict(
			username='adsfisudfioasdfhjlasdfhasjkfhsadjfkhsadfkjasdhfkasjdfhasdjkfa',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')
		self.assertIn(b'Field must be between 4 and 25 characters long.', response.data)

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
		self.assertIn(b'Invalid email address.', response.data)

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
		self.assertIn(b'Passwords must match.', response.data)

	def test_users_register_route_wrong_username(self):
		"""Ensure users register does not allow to register with not correct username"""

		response = self.app.post('/users/register/', data=dict(
			username='(!_)@)#Z<:∆ń∆ń∆śń∆)))',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')
		self.assertIn(b'Username contains illegal characters.', response.data)

	def test_users_register_route_blocked_username(self):
		"""Ensure users register does not allow to register with blocked username"""

		response = self.app.post('/users/register/', data=dict(
			username='admin',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')
		self.assertIn(b'Username is blocked.', response.data)

	def test_users_register_route_user_exists_with_username(self):
		"""Ensure users register does not allow to register when someone exists with username"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()

		response = self.app.post('/users/register/', data=dict(
			username='john',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')
		self.assertIn(b'Username is already in use.', response.data)

	def test_users_register_route_user_exists_with_email(self):
		"""Ensure users register does not allow to register when someone exists with email"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()

		response = self.app.post('/users/register/', data=dict(
			username='johner',
			email='john@example.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/register.html')
		self.assertIn(b'Email is already in use.', response.data)

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

		registered_user = User.query.filter_by(username='tomeker').first()
		self.assertTrue(registered_user is not None)
		self.assertTrue(registered_user.email == 'tomeker@tomekads.com')
		self.assertTrue(check_password_hash(registered_user.password, 'aaaaaa'))

	###
	### ACCOUNT FORM
	###

	def test_users_account_route_requires_login(self):
		"""Ensure users account requires login to be viewed"""

		response = self.app.post('/users/account/', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')
		self.assertIn(b'Please log in to access this page', response.data)

	def test_users_account_route_too_short_username(self):
		"""Ensure users account does not allow to account when username is too short"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='a'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Field must be between 4 and 25 characters long.', response.data)

	def test_users_account_route_too_long_username(self):
		"""Ensure users account does not allow to account when username is too long"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='adsfisudfioasdfhjlasdfhasjkfhsadjfkhsadfkjasdhfkasjdfhasdjkfa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Field must be between 4 and 25 characters long.', response.data)

	def test_users_account_route_wrong_email(self):
		"""Ensure users account does not allow to account with wrong email address"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			email='tomektomek.com'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Invalid email address.', response.data)

	def test_users_account_route_wrong_confirm_password(self):
		"""Ensure users account does not allow to account with wrong confirmed password"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='john',
			email='john@example.com',
			password='aaa',
			confirm='aaaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Passwords must match.', response.data)

	def test_users_account_route_wrong_confirm_password(self):
		"""Ensure users account does not allow to account with wrong confirmed password"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='john',
			email='john@example.com',
			password='aaa',
			confirm='aaa',
			old_password='aaa'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Old password is not correct.', response.data)

	def test_users_account_route_wrong_username(self):
		"""Ensure users account does not allow to account with not correct username"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='(!_)@)#Z<:∆ń∆ń∆śń∆)))',
			email='john@example.com'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Username contains illegal characters.', response.data)

	def test_users_account_route_blocked_username(self):
		"""Ensure users account does not allow to account with blocked username"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='admin',
			email='john@example.com'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Username is blocked.', response.data)

	def test_users_account_route_user_exists_with_username(self):
		"""Ensure users account does not allow to account when someone exists with username"""

		# register user
		self.app.post('/users/register/', data=dict(
			username='tomek',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='tomek',
			email='john@example.com'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Username is already in use.', response.data)

	def test_users_account_route_user_exists_with_email(self):
		"""Ensure users account does not allow to account when someone exists with email"""

		# register user
		self.app.post('/users/register/', data=dict(
			username='tomek',
			email='tomek@tomek.com',
			password='aaa',
			confirm='aaa'
		), follow_redirects=True)

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='john',
			email='tomek@tomek.com'
		), follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'Email is already in use.', response.data)

	def test_users_account_route_account(self):
		"""Ensure users account actually create the user"""

		# add user to database
		user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='tomeker',
			email='tomeker@tomekads.com',
			password='aaaaaa',
			confirm='aaaaaa',
			old_password='a'
		), follow_redirects=True)

		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'The changes have been saved', response.data)

		updated_user = User.query.filter_by(username='tomeker').first()
		self.assertTrue(updated_user is not None)
		self.assertTrue(updated_user.email == 'tomeker@tomekads.com')
		self.assertTrue(check_password_hash(updated_user.password, 'aaaaaa'))

		old_user = User.query.filter_by(username='john').first()
		self.assertTrue(old_user is None)


		# SECOND USER - ONLY USERNAME
		self.logout()

		# add user to database
		second_user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		db.session.add(second_user)
		db.session.commit()
		self.login(email='john@example.com', password='a')

		response = self.app.post('/users/account/', data=dict(
			username='tomekerer',
			email='john@example.com',
			password='',
			confirm='',
			old_password=''
		), follow_redirects=True)

		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/account.html')
		self.assertIn(b'The changes have been saved', response.data)

		updated_user = User.query.filter_by(username='tomekerer').first()
		self.assertTrue(updated_user is not None)
		self.assertTrue(updated_user.email == 'john@example.com')
		self.assertTrue(check_password_hash(updated_user.password, 'a'))
