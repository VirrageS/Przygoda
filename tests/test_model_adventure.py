import os
import unittest

from datetime import datetime, timedelta

from app import app, db

from app.users.models import User
from werkzeug import generate_password_hash

from app.adventures.models import Coordinate, AdventureParticipant
from app.adventures.models import Adventure, AdventureManager
from app.adventures import constants as ADVENTURES

class AdventureTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()

    def test_adventure_creator_id(self):
        adventure = Adventure(
            creator_id=1,
            date=datetime.now(),
            mode=ADVENTURES.AMATEURISH,
            info='Some info today'
        )
        assert adventure.creator_id == 1

    def test_adventure_date(self):
        date = datetime.now()
        adventure = Adventure(
            creator_id=1,
            date=date,
            mode=ADVENTURES.AMATEURISH,
            info='Some info today'
        )
        assert adventure.date == date

    def test_adventure_mode(self):
        adventure = Adventure(
            creator_id=3,
            date=datetime.now(),
            mode=ADVENTURES.AMATEURISH,
            info='Some info today'
        )
        assert adventure.mode == ADVENTURES.AMATEURISH

        self.assertEqual(adventure.get_mode(),
                         ADVENTURES.MODES[ADVENTURES.AMATEURISH])

    def test_adventure_info(self):
        adventure = Adventure(
            creator_id=2,
            date=datetime.now(),
            mode=ADVENTURES.AMATEURISH,
            info='Some info today'
        )
        assert adventure.info == 'Some info today'


class CoordinateTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()

    def test_coordinate_adventure_id(self):
        c = Coordinate(
            adventure_id=1,
            path_point=1,
            latitude=52.229937,
            longitude=21.011380
        )
        assert c.adventure_id == 1

    def test_coordinate_path_point(self):
        c = Coordinate(
            adventure_id=1,
            path_point=1,
            latitude=52.229937,
            longitude=21.011380
        )
        assert c.path_point == 1

    def test_coordinate_latitude(self):
        c = Coordinate(
            adventure_id=1,
            path_point=1,
            latitude=52.229937,
            longitude=21.011380
        )
        assert c.latitude == 52.229937

    def test_coordinate_longitude(self):
        c = Coordinate(
            adventure_id=1,
            path_point=1,
            latitude=52.229937,
            longitude=21.011380
        )
        assert c.longitude == 21.011380


class AdventureParticipantTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app = app.test_client()

    def test_adventure_participant_adventure_id(self):
        a = AdventureParticipant(adventure_id=2, user_id=1)
        assert a.adventure_id == 2
        assert a.user_id == 1

    def test_adventure_participant_user_id(self):
        a = AdventureParticipant(adventure_id=1, user_id=2)
        assert a.adventure_id == 1
        assert a.user_id == 2

class AdventureManagerTestCase(unittest.TestCase):
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

    def test_adventure_manager_get_adventures(self):
        ids = [1,2,3,4,5]
        for cid in ids:
            adventure = Adventure(
                creator_id=cid,
                date=datetime.now() + timedelta(minutes=-9),
                mode=ADVENTURES.RECREATIONAL,
                info='Some info today'
            )

            db.session.add(adventure)
            db.session.commit()

        adventures = Adventure.objects.adventures()
        assert adventures is not None
        assert len(adventures) == len(ids)

        for adventure in adventures:
            assert adventure is not None
            assert adventure.creator_id in ids


    def test_adventure_manager_get_active_adventures(self):
        active = [1,2]
        non_active = [3,4,5]

        for cid in non_active:
            adventure = Adventure(
                creator_id=cid,
                date=datetime.now() + timedelta(minutes=-9),
                mode=ADVENTURES.RECREATIONAL,
                info='Some info today'
            )

            db.session.add(adventure)
            db.session.commit()

        for cid in active:
            adventure = Adventure(
                creator_id=cid,
                date=datetime.now() + timedelta(minutes=9),
                mode=ADVENTURES.RECREATIONAL,
                info='Info'
            )

            db.session.add(adventure)
            db.session.commit()

        active_adventures = Adventure.objects.active_adventures()
        all_adventures = Adventure.objects.adventures()

        self.assertIsNotNone(active_adventures, msg=None)
        self.assertIsNotNone(all_adventures, msg=None)
        self.assertEqual(len(active_adventures), len(active), msg=None)
        self.assertEqual(len(all_adventures), len(active) + len(non_active))

        for adventure in active_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertIn(adventure.creator_id, active, msg=None)

        for adventure in all_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertIn(adventure.creator_id, (active + non_active))


    def test_adventure_manager_get_user_adventures(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )

        db.session.add(user)
        db.session.commit()

        # user's adventures
        for i in range(1, 5):
            adventure = Adventure(
                creator_id=user.id,
                date=datetime.now() + timedelta(minutes=9),
                mode=ADVENTURES.RECREATIONAL,
                info='Info'
            )

            db.session.add(adventure)
            db.session.commit()

        # not user's adventures
        for i in range(1, 5):
            adventure = Adventure(
                creator_id=user.id + 1,
                date=datetime.now() + timedelta(minutes=9),
                mode=ADVENTURES.RECREATIONAL,
                info='Info'
            )

            db.session.add(adventure)
            db.session.commit()

        user_adventures = Adventure.objects.user_adventures(user.id)
        all_adventures = Adventure.objects.adventures()

        self.assertIsNotNone(user_adventures, msg=None)
        self.assertIsNotNone(all_adventures, msg=None)
        self.assertGreater(len(all_adventures), len(user_adventures))

        for adventure in user_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertEqual(adventure.creator_id, user.id, msg=None)


    def test_adventure_manager_get_user_active_adventures(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@example.com'
        )

        db.session.add(user)
        db.session.commit()

        # user's active adventures
        for i in range(1, 5):
            adventure = Adventure(
                creator_id=user.id,
                date=datetime.now() + timedelta(minutes=9),
                mode=ADVENTURES.RECREATIONAL,
                info='active'
            )

            db.session.add(adventure)
            db.session.commit()

        # user's non active adventures
        for i in range(1, 5):
            adventure = Adventure(
                creator_id=user.id,
                date=datetime.now() + timedelta(minutes=-9),
                mode=ADVENTURES.RECREATIONAL,
                info='non_active'
            )

            db.session.add(adventure)
            db.session.commit()

        # not user's adventures
        for i in range(1, 5):
            adventure = Adventure(
                creator_id=user.id + 1,
                date=datetime.now() + timedelta(minutes=9),
                mode=ADVENTURES.RECREATIONAL,
                info='Info'
            )

            db.session.add(adventure)
            db.session.commit()

        user_adventures = Adventure.objects.user_adventures(user.id)
        user_active_adventures = Adventure.objects.user_active_adventures(user.id)
        all_adventures = Adventure.objects.adventures()

        self.assertIsNotNone(user_adventures, msg=None)
        self.assertIsNotNone(user_active_adventures, msg=None)
        self.assertIsNotNone(all_adventures, msg=None)
        self.assertGreater(len(all_adventures), len(user_adventures))
        self.assertNotEqual(user_adventures, user_active_adventures, msg=None)

        for adventure in user_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertEqual(adventure.creator_id, user.id, msg=None)
            self.assertIn(adventure.info, ['active', 'non_active'], msg=None)

        for adventure in user_active_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertEqual(adventure.creator_id, user.id, msg=None)
            self.assertEqual(adventure.info, 'active', msg=None)

    def test_adventure_manager_get_coordinates(self):
        pass

    def test_adventure_manager_get_participants(self):
        pass

    def test_adventure_manager_get_active_participants(self):
        pass

    def test_adventure_manager_get_user_joined_adventures(self):
        pass

    def test_adventure_manager_get_user_active_joined_adventures(self):
        pass
