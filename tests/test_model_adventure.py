import os
import unittest

from datetime import datetime
from app import app
from app.adventures.models import Adventure

class AdventureTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		self.app = app.test_client()

	def test_adventure_date(self):
		a = Adventure(user='john', date=datetime.utcnow(), info='Some info today', joined=10)
		assert a.date != datetime.utcnow()

	def test_adventure_info(self):
		a = Adventure(user='john', date=datetime.utcnow(), info='Some info today', joined=10)
		assert a.info == 'Some info today'

	def test_adventure_joined(self):
		a = Adventure(user='john', date=datetime.utcnow(), info='Some info today', joined=10)
		assert a.joined == 10

if __name__ == '__main__':
	unittest.main()
