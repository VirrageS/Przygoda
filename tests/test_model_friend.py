import os
import unittest

from datetime import datetime
from app import app, db
from app.friends.models import Friend
from app.friends.models import FriendshipRequest, FriendshipManager


class FriendTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()

    def test_friend_from_user(self):
        friend = Friend(from_user=1, to_user=2)
        self.assertEqual(friend.from_user, 1)

    def test_friend_to_user(self):
        friend = Friend(from_user=2, to_user=1123)
        self.assertEqual(friend.to_user, 1123)

class FriendshipManagerTestCase(unittest.TestCase):
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

    def test_friendship_manager_get_all_user_friends(self):
        pass
