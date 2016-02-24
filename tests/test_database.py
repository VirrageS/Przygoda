import os
import unittest

from datetime import datetime, timedelta
from config import base_dir
from werkzeug import check_password_hash, generate_password_hash

from app import app, db
from app.friends.models import Friend, FriendshipRequest
from app.users.models import User
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES

class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.app.post('/users/login/', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/users/logout/', follow_redirects=True)

    def test_add_adventure_to_database(self):
        a = Adventure(creator_id=2, date=datetime.now(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()
        a = Adventure.query.filter_by(creator_id=2).first()
        assert a.mode == ADVENTURES.RECREATIONAL
        assert a.info == 'Some info today'

        a = Adventure(creator_id=2, date=datetime.now(), mode=ADVENTURES.AMATEURISH, info='Some info today')
        db.session.add(a)
        db.session.commit()
        assert a.mode == ADVENTURES.AMATEURISH

        b = Adventure.query.filter_by(creator_id=2).all()
        assert len(b) == 2

    def test_add_user_to_database(self):
        user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(username='john').first()
        assert user.id == 1
        assert user.username == 'john'
        assert check_password_hash(user.password, 'a')
        assert user.email == 'john@example.com'
        self.assertIn("facebook$" + user.username, user.social_id)
        assert user.registered_on is not None
        assert user.confirmed is False
        assert user.confirmed_on is None
        self.assertTrue(user.first_login is None)
        self.assertTrue(user.last_login is None)
        self.assertFalse(user.is_active_login())

        user.update_login_info()
        login_date = datetime.now()

        self.assertTrue(user.first_login is not None)
        self.assertLess(user.first_login, login_date)
        self.assertTrue(user.last_login is not None)
        self.assertLess(user.last_login, login_date)

        self.assertTrue(user.is_active_login())
        user.last_login = datetime.now() + timedelta(days=-10)
        db.session.add(user)
        db.session.commit()
        self.assertFalse(user.is_active_login())

        # login again
        user.update_login_info()

        self.assertTrue(user.first_login is not None)
        self.assertLess(user.first_login, login_date)
        self.assertTrue(user.last_login is not None)
        self.assertGreater(user.last_login, login_date)

        user_second = User(username='johner', password=generate_password_hash('a'), email='susan@examplee.com')
        db.session.add(user_second)
        db.session.commit()

        user_second = User.query.filter_by(username='johner').first()
        assert user_second.id == 2
        self.assertEqual(user_second.id, 2)
        self.assertNotEqual(user_second.username, 'john', msg=None)
        self.assertEqual(user_second.username, 'johner')

    def test_add_coordinate_to_database(self):
        """Testing adding cordinantes of adventure to database.
        Main thing is that we have to check if float is begin serialized properly"""

        c = Coordinate(adventure_id=1, path_point=10, latitude=52.229937, longitude=21.011380)
        db.session.add(c)
        db.session.commit()

        c = Coordinate.query.filter_by(adventure_id=1).first()
        assert c is not None
        assert c.path_point == 10
        assert c.latitude == 52.229937
        assert c.longitude == 21.011380

    def test_add_adventure_participant_to_database(self):
        """Testing adding adventure participant to database"""

        participant = AdventureParticipant(adventure_id=1, user_id=1)
        db.session.add(participant)
        db.session.commit()

        participant = AdventureParticipant.query.filter_by(
            adventure_id=1).first()
        self.assertIsNotNone(participant, msg=None)
        self.assertEqual(participant.user_id, 1)

    def test_add_friend_to_database(self):
        """Testing adding friend to database"""

        friend = Friend(from_user=1, to_user=2)
        db.session.add(friend)
        db.session.commit()

        friend = Friend.query.filter_by(from_user=1, to_user=2).first()
        self.assertIsNotNone(friend, msg=None)
        self.assertEqual(friend.from_user, 1, msg=None)
        self.assertEqual(friend.to_user, 2, msg=None)

    def test_add_friendship_request_to_database(self):
        """Testing adding friendship request to database"""

        request = FriendshipRequest(from_user=1, to_user=2)
        db.session.add(request)
        db.session.commit()

        request = FriendshipRequest.query.filter_by(from_user=1, to_user=2).first()
        self.assertIsNotNone(request, msg=None)
        self.assertEqual(request.from_user, 1, msg=None)
        self.assertEqual(request.to_user, 2, msg=None)
