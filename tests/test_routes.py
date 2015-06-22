import unittest
from flask import Flask
from flask.ext.testing import TestCase

from app import app

class RoutesTestCase(TestCase, unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		self.app = app.test_client()

	def create_app(self):
		app = Flask(__name__)
		app.config['TESTING'] = True
		# Default port is 5000
		app.config['LIVESERVER_PORT'] = 8943
		return app

	def test_adventures_new_route_requires_login(self):
		# Ensure adventures new route requires a logged in user.
		response = self.app.get('/adventures/new', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')
