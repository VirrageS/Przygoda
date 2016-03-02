import os
import unittest

from datetime import datetime, timedelta

from app.users.models import User
from werkzeug import check_password_hash, generate_password_hash

from app.adventures.models import Adventure
from app.adventures import constants as ADVENTURES


from app.recommender_system import get_adventures_by_user_position
# from app.recommender_system import get_adventures_by_user_position
from app import app, db

class RecommenderSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()
        db.create_all()

        self.user_tom = self.add_user()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True

        # Default port is 5000
        app.config['LIVESERVER_PORT'] = 8943
        return app

    def add_user(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )

        db.session.add(user)
        db.session.commit()

        # add adventures
        for i in range(0, 10):
            adventure = Adventure(
                creator_id=user.id,
                date=datetime.now() + timedelta(minutes=9 * (i + 1)),
                mode=ADVENTURES.AMATEURISH,
                info='Some info today'
            )

            db.session.add(adventure)
            db.session.commit()

        return user

    def test_get_adventures_by_user_position_no_position(self):
        position = None

        adventures = get_adventures_by_user_position(self.user_tom.id, position)
        self.assertIsNone(adventures)

        created_adventures = Adventure.objects.user_active_adventures(self.user_tom.id)
        self.assertIsNotNone(created_adventures, msg=None)
