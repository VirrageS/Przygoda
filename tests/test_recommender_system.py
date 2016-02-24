import os
import unittest

from datetime import datetime, timedelta

from app import app, db

class RecommenderSystemTestCase(unittest.TestCase):
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

    def test_something(self):
        pass
