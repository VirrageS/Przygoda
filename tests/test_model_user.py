import unittest

from app import app
from app.users.models import User

class UserTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		self.app = app.test_client()

	def test_user_username(self):
		u = User(username='john', password='a', email='john@example.com')
		assert u.username == 'john'

	def test_user_password(self):
		u = User(username='john', password='a', email='john@example.com')
		assert u.password == 'a'

	def test_user_email(self):
		u = User(username='john', password='a', email='john@example.com')
		assert u.email == 'john@example.com'
