import unittest

from app import app

class RoutesTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		self.app = app.test_client()

	def test_adventures_new_route_requires_login(self):
		# Ensure adventures new route requires a logged in user.
		response = self.client.get('/adventures/new', follow_redirects=True)
		self.assertTrue(response.status_code == 200)
		self.assertTemplateUsed('users/login.html')
