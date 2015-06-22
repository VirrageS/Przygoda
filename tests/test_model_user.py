import unittest

from app import app
from werkzeug import check_password_hash, generate_password_hash
from app.users.models import User

class UserTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		self.app = app.test_client()

	def test_user_username(self):
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		assert u.username == 'john'

	def test_user_password(self):
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		assert check_password_hash(u.password, 'a')

	def test_user_email(self):
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		assert u.email == 'john@example.com'

	def test_user_confirmed(self):
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		assert u.confirmed == False

	def test_user_confirmed_on(self):
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		assert u.confirmed_on is None

	def test_user_registered_on(self):
		u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
		assert u.registered_on is not None
