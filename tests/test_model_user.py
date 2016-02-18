import unittest

from app import app
from werkzeug import check_password_hash, generate_password_hash
from app.users.models import User
from app.users import constants as USER

class UserTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()

    def test_user_username(self):
        u = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )
        assert u.username == 'john'

    def test_user_password(self):
        u = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )
        assert check_password_hash(u.password, 'a')

    def test_user_email(self):
        u = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )
        assert u.email == 'john@example.com'

    def test_user_social_id(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )
        self.assertIn('facebook$john', user.social_id)

        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com',
            social_id='facebok$sadfaksdfjasd'
        )
        self.assertEqual(user.social_id, 'facebok$sadfaksdfjasd')

    def test_user_confirmed(self):
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        assert u.confirmed == False

    def test_user_confirmed_on(self):
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        assert u.confirmed_on is None

    def test_user_registered_on(self):
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        assert u.registered_on is not None

    def test_user_role(self):
        user = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        self.assertEqual(user.role, USER.USER)

        self.assertEqual(user.get_role(), USER.ROLE[USER.USER])
        self.assertFalse(user.is_admin())

        user.role = USER.ADMIN
        self.assertEqual(user.get_role(), USER.ROLE[USER.ADMIN])
        self.assertTrue(user.is_admin())
