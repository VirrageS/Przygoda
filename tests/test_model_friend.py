import os
import unittest

from datetime import datetime

from app import app, db
from app.users.models import User
from werkzeug import generate_password_hash

from app.friends.models import Friend
from app.friends.models import FriendshipRequest, FriendshipManager
from app.friends.exceptions import ValidationError, AlreadyFriendsError
from app.friends.exceptions import AlreadyExistsError


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

        self.user_pw = 'test'
        self.user_bob = self.create_user('bob', 'bob@bob.com', self.user_pw)
        self.user_steve = self.create_user('steve', 'steve@steve.com', self.user_pw)
        self.user_susan = self.create_user('susan', 'susan@susan.com', self.user_pw)
        self.user_amy = self.create_user('amy', 'amy@amy.amy.com', self.user_pw)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True

        # Default port is 5000
        app.config['LIVESERVER_PORT'] = 8943
        return app

    def create_user(self, username, email, password):
        user = User(
            username=username,
            password=generate_password_hash(password),
            email=email
        )

        db.session.add(user)
        db.session.commit()
        return user.id

    def test_friendship_manager_make_friends(self):
        user1 = User(
            username='john1',
            password=generate_password_hash('a'),
            email='john1@example.com'
        )

        user2 = User(
            username='john2',
            password=generate_password_hash('a'),
            email='john2@example.com'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        Friend.objects.make_friends(user1.id, user2.id)

        are_friends = Friend.objects.are_friends(user1.id, user2.id)
        self.assertTrue(are_friends)

        requests = Friend.objects.requests(user1.id)
        self.assertEqual(requests, [], msg=None)

        requests = Friend.objects.requests(user2.id)
        self.assertEqual(requests, [], msg=None)

    def test_friendship_manager_make_friends_same_person(self):
        user1 = User(
            username='john1',
            password=generate_password_hash('a'),
            email='john1@example.com'
        )

        db.session.add(user1)
        db.session.commit()

        try:
            Friend.objects.make_friends(user1.id, user1.id)
            self.assertTrue(False, "They should not be friends")
        except ValidationError:
            self.assertTrue(True)

        friends = Friend.objects.friends(user1.id)
        self.assertEqual(friends, [], msg=None)

    def test_friendship_manager_make_friends_are_already_friends(self):
        user1 = User(
            username='john1',
            password=generate_password_hash('a'),
            email='john1@example.com'
        )

        user2 = User(
            username='john2',
            password=generate_password_hash('a'),
            email='john2@example.com'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        Friend.objects.make_friends(user1.id, user2.id)

        are_friends = Friend.objects.are_friends(user1.id, user2.id)
        self.assertTrue(are_friends)

        try:
            Friend.objects.make_friends(user1.id, user2.id)
            self.assertTrue(False, "They are already friends, so...")
        except AlreadyFriendsError:
            self.assertTrue(True)

        are_friends = Friend.objects.are_friends(user1.id, user2.id)
        self.assertTrue(are_friends)

        friends = Friend.objects.friends(user1.id)
        self.assertIsNotNone(friends, msg=None)
        self.assertEqual(len(friends), 1, msg=None)

    def test_friendship_manager_are_friends(self):
        user1 = User(
            username='john1',
            password=generate_password_hash('a'),
            email='john1@example.com'
        )

        user2 = User(
            username='john2',
            password=generate_password_hash('a'),
            email='john2@example.com'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        are_friends = Friend.objects.are_friends(user1.id, user2.id)
        self.assertFalse(are_friends, msg=None)

        Friend.objects.make_friends(user1.id, user2.id)

        are_friends = Friend.objects.are_friends(user1.id, user2.id)
        self.assertTrue(are_friends, msg=None)

    def test_friendship_manager_get_all_user_friends(self):
        main_user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )

        db.session.add(main_user)
        db.session.commit()

        friends_number = 10
        for i in range(0, friends_number):
            user = User(
                username='john'+str(i),
                password=generate_password_hash('a'),
                email='john@example.com'+str(i)
            )

            db.session.add(user)
            db.session.commit()

            Friend.objects.make_friends(main_user.id, user.id)

        not_friends_number = 5
        for i in range(0, not_friends_number):
            user = User(
                username='john1'+str(i),
                password=generate_password_hash('a'),
                email='john2@example.com'+str(i)
            )

            db.session.add(user)
            db.session.commit()

        friends = Friend.objects.friends(main_user.id)
        self.assertIsNotNone(friends, msg=None)
        self.assertEqual(len(friends), friends_number, msg=None)

        for friend in friends:
            self.assertIsNotNone(friend, msg=None)
            self.assertIsInstance(friend, User)

    def test_friendship_request(self):
        ### Bob wants to be friends with Steve
        req1 = Friend.objects.add_friend(self.user_bob, self.user_steve)

        # Ensure neither have friends already
        self.assertEqual(Friend.objects.friends(self.user_bob), [])
        self.assertEqual(Friend.objects.friends(self.user_steve), [])

        # Ensure FriendshipRequest is created
        self.assertEqual(FriendshipRequest.query.filter_by(
            from_user=self.user_bob).count(), 1)
        self.assertEqual(FriendshipRequest.query.filter_by(
            to_user=self.user_steve).count(), 1)
        self.assertEqual(Friend.objects.unread_request_count(self.user_steve), 1)

        # Ensure the proper sides have requests or not
        self.assertEqual(len(Friend.objects.requests(self.user_bob)), 0)
        self.assertEqual(len(Friend.objects.requests(self.user_steve)), 1)
        self.assertEqual(len(Friend.objects.sent_requests(self.user_bob)), 1)
        self.assertEqual(len(Friend.objects.sent_requests(self.user_steve)), 0)

        self.assertEqual(len(Friend.objects.unread_requests(self.user_steve)), 1)
        self.assertEqual(Friend.objects.unread_request_count(self.user_steve), 1)

        self.assertEqual(len(Friend.objects.rejected_requests(self.user_steve)), 0)

        unrejected = len(Friend.objects.unrejected_requests(self.user_steve))
        self.assertEqual(unrejected, 1)

        unrejected = Friend.objects.unrejected_request_count(self.user_steve)
        self.assertEqual(unrejected, 1)

        # Ensure they aren't friends at this point
        self.assertFalse(Friend.objects.are_friends(self.user_bob, self.user_steve))

        # Accept the request
        req1.accept()

        # Ensure neither have pending requests
        self.assertEqual(FriendshipRequest.query.filter_by(
            from_user=self.user_bob).count(), 0)
        self.assertEqual(FriendshipRequest.query.filter_by(
            to_user=self.user_steve).count(), 0)

        # Ensure both are in each other's friend lists
        friends = [user.id for user in Friend.objects.friends(self.user_bob)]
        self.assertEqual(friends, [self.user_steve])

        friends = [user.id for user in Friend.objects.friends(self.user_steve)]
        self.assertEqual(friends, [self.user_bob])

        are_friends = Friend.objects.are_friends(self.user_bob, self.user_steve)
        self.assertTrue(are_friends)

        # Make sure we can remove friendship
        removed = Friend.objects.remove_friend(self.user_bob, self.user_steve)
        self.assertTrue(removed)

        are_friends = Friend.objects.are_friends(self.user_bob, self.user_steve)
        self.assertFalse(are_friends)

        removed = Friend.objects.remove_friend(self.user_bob, self.user_steve)
        self.assertFalse(removed)

        # Susan wants to be friends with Amy, but cancels it
        req2 = Friend.objects.add_friend(self.user_susan, self.user_amy)
        self.assertEqual(Friend.objects.friends(self.user_susan), [])
        self.assertEqual(Friend.objects.friends(self.user_amy), [])
        req2.cancel()
        self.assertEqual(Friend.objects.requests(self.user_susan), [])
        self.assertEqual(Friend.objects.requests(self.user_amy), [])

        # Susan wants to be friends with Amy, but Amy rejects it
        req3 = Friend.objects.add_friend(self.user_susan, self.user_amy)
        self.assertEqual(Friend.objects.friends(self.user_susan), [])
        self.assertEqual(Friend.objects.friends(self.user_amy), [])
        req3.reject()

        # Duplicated requests raise a more specific subclass of IntegrityError.
        with self.assertRaises(AlreadyExistsError):
            Friend.objects.add_friend(self.user_susan, self.user_amy)

        are_friends = Friend.objects.are_friends(self.user_susan, self.user_amy)
        self.assertFalse(are_friends)
        self.assertEqual(len(Friend.objects.rejected_requests(self.user_amy)), 1)
        self.assertEqual(len(Friend.objects.rejected_requests(self.user_amy)), 1)

        # let's try that again..
        req3.cancel()

        # Susan wants to be friends with Amy, and Amy reads it
        req4 = Friend.objects.add_friend(self.user_susan, self.user_amy)
        req4.mark_viewed()

        are_friends = Friend.objects.are_friends(self.user_susan, self.user_amy)
        self.assertFalse(are_friends)
        self.assertEqual(len(Friend.objects.read_requests(self.user_amy)), 1)

        # Ensure we can't be friends with ourselves
        with self.assertRaises(ValidationError):
            Friend.objects.add_friend(self.user_bob, self.user_bob)

    def test_already_friends_with_request(self):
        # Make Bob and Steve friends
        req = Friend.objects.add_friend(self.user_bob, self.user_steve)
        req.accept()

        with self.assertRaises(AlreadyFriendsError):
            req2 = Friend.objects.add_friend(self.user_bob, self.user_steve)

    def test_multiple_friendship_requests(self):
        """ Ensure multiple friendship requests are handled properly """
        ### Bob wants to be friends with Steve
        req1 = Friend.objects.add_friend(self.user_bob, self.user_steve)

        # Ensure neither have friends already
        self.assertEqual(Friend.objects.friends(self.user_bob), [])
        self.assertEqual(Friend.objects.friends(self.user_steve), [])

        # Ensure FriendshipRequest is created
        self.assertEqual(FriendshipRequest.query.filter_by(
            from_user=self.user_bob).count(), 1)
        self.assertEqual(FriendshipRequest.query.filter_by(
            to_user=self.user_steve).count(), 1)
        self.assertEqual(Friend.objects.unread_request_count(self.user_steve),
                         1)

        # Steve also wants to be friends with Bob before Bob replies
        req2 = Friend.objects.add_friend(self.user_steve, self.user_bob)

        # Ensure they aren't friends at this point
        are_friends = Friend.objects.are_friends(self.user_bob, self.user_steve)
        self.assertFalse(are_friends)

        # Accept the request
        req1.accept()

        # Ensure neither have pending requests
        self.assertEqual(FriendshipRequest.query.filter_by(
            from_user=self.user_bob).count(), 0)
        self.assertEqual(FriendshipRequest.query.filter_by(
            to_user=self.user_steve).count(), 0)
        self.assertEqual(FriendshipRequest.query.filter_by(
            from_user=self.user_steve).count(), 0)
        self.assertEqual(FriendshipRequest.query.filter_by(
            to_user=self.user_bob).count(), 0)

    def test_multiple_calls_add_friend(self):
        """Ensure multiple calls with same friends,
        but different message works as expected"""
        req1 = Friend.objects.add_friend(self.user_bob, self.user_steve)

        with self.assertRaises(AlreadyExistsError):
            req2 = Friend.objects.add_friend(self.user_bob, self.user_steve)

    # def test_following(self):
    #     # Bob follows Steve
    #     req1 = Follow.objects.add_follower(self.user_bob, self.user_steve)
    #     self.assertEqual(len(Follow.objects.followers(self.user_steve)), 1)
    #     self.assertEqual(len(Follow.objects.following(self.user_bob)), 1)
    #     self.assertEqual(Follow.objects.followers(self.user_steve), [self.user_bob])
    #     self.assertEqual(Follow.objects.following(self.user_bob), [self.user_steve])
    #
    #     self.assertTrue(Follow.objects.follows(self.user_bob, self.user_steve))
    #     self.assertFalse(Follow.objects.follows(self.user_steve, self.user_bob))
    #
    #     # Duplicated requests raise a more specific subclass of IntegrityError.
    #     with self.assertRaises(IntegrityError):
    #         Follow.objects.add_follower(self.user_bob, self.user_steve)
    #     with self.assertRaises(AlreadyExistsError):
    #         Follow.objects.add_follower(self.user_bob, self.user_steve)
    #
    #     # Remove the relationship
    #     self.assertTrue(Follow.objects.remove_follower(self.user_bob, self.user_steve))
    #     self.assertEqual(len(Follow.objects.followers(self.user_steve)), 0)
    #     self.assertEqual(len(Follow.objects.following(self.user_bob)), 0)
    #     self.assertFalse(Follow.objects.follows(self.user_bob, self.user_steve))
    #
    #     # Ensure we canot follow ourselves
    #     with self.assertRaises(ValidationError):
    #         Follow.objects.add_follower(self.user_bob, self.user_bob)
    #
    #     with self.assertRaises(ValidationError):
    #         Follow.objects.create(follower=self.user_bob, followee=self.user_bob)
