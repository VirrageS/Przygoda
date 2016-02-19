import os
import unittest

from datetime import datetime, timedelta

from app import app, db

from app.users.models import User
from werkzeug import generate_password_hash

from app.adventures.models import Coordinate, AdventureParticipant
from app.adventures.models import Adventure, AdventureManager
from app.adventures.exceptions import AlreadyParticipantError
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
            self.assertIsInstance(adventure, Adventure, msg=None)
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
            self.assertIsInstance(adventure, Adventure, msg=None)
            self.assertEqual(adventure.creator_id, user.id, msg=None)
            self.assertIn(adventure.info, ['active', 'non_active'], msg=None)

        for adventure in user_active_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertIsInstance(adventure, Adventure, msg=None)
            self.assertEqual(adventure.creator_id, user.id, msg=None)
            self.assertTrue(adventure.is_active(), msg=None)

    def test_adventure_manager_get_coordinates(self):
        adventure = Adventure(
            creator_id=1,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='Info'
        )

        db.session.add(adventure)
        db.session.commit()

        coordinates_number = 10
        for i in range(0, coordinates_number):
            coordinate = Coordinate(
                adventure_id=adventure.id,
                path_point=i,
                latitude=10.234,
                longitude=34.3242
            )

            db.session.add(coordinate)
            db.session.commit()

        coordinates = Adventure.objects.coordinates(adventure.id)

        self.assertIsNotNone(coordinates, msg=None)
        self.assertEqual(len(coordinates), coordinates_number, msg=None)

        for coordinate in coordinates:
            self.assertIsNotNone(coordinate, msg=None)
            self.assertIsInstance(coordinate, Coordinate, msg=None)


    def test_adventure_manager_get_participants(self):
        adventure = Adventure(
            creator_id=1,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='Info'
        )

        db.session.add(adventure)
        db.session.commit()

        participants_number = 10
        for i in range(0, participants_number):
            user = User(
                username='john'+str(i),
                password=generate_password_hash('a'),
                email='john@example.com'+str(i)
            )

            db.session.add(user)
            db.session.commit()

            participant = AdventureParticipant(
                adventure_id=adventure.id,
                user_id=user.id
            )

            db.session.add(participant)
            db.session.commit()

        participants = Adventure.objects.participants(adventure.id)

        self.assertIsNotNone(participants, msg=None)
        self.assertEqual(len(participants), participants_number, msg=None)

        for participant in participants:
            self.assertIsNotNone(participant, msg=None)
            self.assertIsInstance(participant, User, msg=None)

    def test_adventure_manager_get_active_participants(self):
        adventure = Adventure(
            creator_id=1,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='Info'
        )

        db.session.add(adventure)
        db.session.commit()

        non_active_number = 10
        for i in range(0, non_active_number):
            user = User(
                username='john'+str(i),
                password=generate_password_hash('a'),
                email='john@example.com'+str(i)
            )

            db.session.add(user)
            db.session.commit()

            participant = AdventureParticipant(
                adventure_id=adventure.id,
                user_id=user.id
            )

            participant.left_on = datetime.now() + timedelta(minutes=-9)

            db.session.add(participant)
            db.session.commit()

        active_number = 10
        for i in range(0, active_number):
            user = User(
                username='asdf'+str(i),
                password=generate_password_hash('a'),
                email='asdf@example.com'+str(i)
            )

            db.session.add(user)
            db.session.commit()

            added = Adventure.objects.add_participant(adventure.id, user.id)
            self.assertTrue(added, msg=None)


        all_participants = Adventure.objects.participants(adventure.id)
        self.assertIsNotNone(all_participants, msg=None)
        self.assertEqual(len(all_participants), non_active_number + active_number)

        active_participants = Adventure.objects.active_participants(adventure.id)
        self.assertIsNotNone(active_participants, msg=None)
        self.assertEqual(len(active_participants), active_number, msg=None)

        for participant in all_participants:
            self.assertIsNotNone(participant, msg=None)
            self.assertIsInstance(participant, User, msg=None)

        for participant in active_participants:
            self.assertIsNotNone(participant, msg=None)
            self.assertIsInstance(participant, User, msg=None)
            self.assertIn('asdf', participant.username, msg=None)

    def test_adventure_manager_get_user_joined_adventures(self):
        adventures_number = 10
        for i in range(0, adventures_number):
            adventure = Adventure(
                creator_id=1,
                date=datetime.now() + timedelta(minutes=9),
                mode=ADVENTURES.RECREATIONAL,
                info='Info'
            )

            db.session.add(adventure)
            db.session.commit()

        adventures = Adventure.objects.adventures()

        user = User(
            username='asdf'+str(i),
            password=generate_password_hash('a'),
            email='asdf@example.com'+str(i)
        )

        db.session.add(user)
        db.session.commit()

        joined_adventures_number = 5
        for i in range(0, joined_adventures_number):
            added = Adventure.objects.add_participant(adventures[i].id, user.id)
            self.assertTrue(added, msg=None)


        joined_adventures = Adventure.objects.user_joined_adventures(user.id)
        self.assertIsNotNone(joined_adventures, msg=None)
        self.assertEqual(len(joined_adventures), joined_adventures_number)

        for adventure in joined_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertIsInstance(adventure, Adventure, msg=None)

    def test_adventure_manager_get_user_joined_active_adventures(self):
        adventures_number = 20
        for i in range(0, adventures_number):
            adventure = Adventure(
                creator_id=1,
                date=datetime.now() + timedelta(minutes=-9),
                mode=ADVENTURES.RECREATIONAL,
                info='not_active'
            )

            db.session.add(adventure)
            db.session.commit()

        active_adventures_number = 10
        for i in range(0, active_adventures_number):
            adventure = Adventure(
                creator_id=1,
                date=datetime.now() + timedelta(minutes=9),
                mode=ADVENTURES.RECREATIONAL,
                info='active'
            )

            db.session.add(adventure)
            db.session.commit()

        adventures = Adventure.objects.adventures()
        active_adventures = Adventure.objects.active_adventures()

        user = User(
            username='asdf'+str(i),
            password=generate_password_hash('a'),
            email='asdf@example.com'+str(i)
        )

        db.session.add(user)
        db.session.commit()

        joined_adventures_number = 10
        for i in range(0, joined_adventures_number):
            added = Adventure.objects.add_participant(adventures[i].id, user.id)
            self.assertTrue(added, msg=None)

        joined_active_adventures_number = 5
        for i in range(0, joined_active_adventures_number):
            added = Adventure.objects.add_participant(active_adventures[i].id,
                                                      user.id)
            self.assertTrue(added, msg=None)

        joined_adventures = Adventure.objects.user_joined_adventures(user.id)
        self.assertIsNotNone(joined_adventures, msg=None)

        joined_active_adventures = Adventure.objects.user_joined_active_adventures(user.id)
        self.assertIsNotNone(joined_active_adventures, msg=None)
        self.assertEqual(len(joined_active_adventures),
                         joined_active_adventures_number)

        for adventure in joined_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertIsInstance(adventure, Adventure, msg=None)

        for adventure in joined_active_adventures:
            self.assertIsNotNone(adventure, msg=None)
            self.assertIsInstance(adventure, Adventure, msg=None)
            self.assertTrue(adventure.is_active(), msg=None)


    def test_adventure_manager_add_participant(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@johner.com'
        )

        adventure = Adventure(
            creator_id=10,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='active'
        )

        db.session.add(adventure)
        db.session.add(user)
        db.session.commit()

        added = Adventure.objects.add_participant(adventure.id, user.id)
        self.assertTrue(added, msg=None)

        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure.id,
            user_id=user.id
        ).first()

        self.assertIsNotNone(participant, msg=None)
        self.assertTrue(participant.is_active(), msg=None)

    def test_adventure_manager_add_participant_alread_joined(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@johner.com'
        )

        adventure = Adventure(
            creator_id=10,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='active'
        )

        db.session.add(adventure)
        db.session.add(user)
        db.session.commit()

        added = Adventure.objects.add_participant(adventure.id, user.id)
        self.assertTrue(added, msg=None)

        try:
            Adventure.objects.add_participant(adventure.id, user.id)
            self.assertTrue(False, msg="User should not be added...")
        except AlreadyParticipantError:
            self.assertTrue(True, msg=None)

    def test_adventure_manager_add_participant_left(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@johner.com'
        )

        adventure = Adventure(
            creator_id=10,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='active'
        )

        db.session.add(adventure)
        db.session.add(user)
        db.session.commit()

        added = Adventure.objects.add_participant(adventure.id, user.id)
        removed = Adventure.objects.remove_participant(adventure.id, user.id)
        self.assertTrue(added, msg=None)
        self.assertTrue(removed, msg=None)

        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure.id,
            user_id=user.id
        ).first()

        self.assertIsNotNone(participant, msg=None)
        self.assertFalse(participant.is_active(), msg=None)

        added = Adventure.objects.add_participant(adventure.id, user.id)
        self.assertTrue(added, msg=None)

        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure.id,
            user_id=user.id
        ).first()

        self.assertIsNotNone(participant, msg=None)
        self.assertTrue(participant.is_active(), msg=None)

    def test_adventure_manager_remove_participant(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@johner.com'
        )

        adventure = Adventure(
            creator_id=10,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='active'
        )

        db.session.add(adventure)
        db.session.add(user)
        db.session.commit()

        added = Adventure.objects.add_participant(adventure.id, user.id)
        removed = Adventure.objects.remove_participant(adventure.id, user.id)
        self.assertTrue(added, msg=None)
        self.assertTrue(removed, msg=None)

        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure.id,
            user_id=user.id
        ).first()

        self.assertIsNotNone(participant, msg=None)
        self.assertFalse(participant.is_active(), msg=None)


    def test_adventure_manager_remove_participant_not_existing(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@johner.com'
        )

        adventure = Adventure(
            creator_id=10,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='active'
        )

        db.session.add(adventure)
        db.session.add(user)
        db.session.commit()

        removed = Adventure.objects.remove_participant(adventure.id, user.id)
        self.assertFalse(removed, msg=None)

    def test_adventure_manager_remove_participant_left(self):
        user = User(
            username='john',
            password=generate_password_hash('a'),
            email='john@johner.com'
        )

        adventure = Adventure(
            creator_id=10,
            date=datetime.now() + timedelta(minutes=9),
            mode=ADVENTURES.RECREATIONAL,
            info='active'
        )

        db.session.add(adventure)
        db.session.add(user)
        db.session.commit()

        added = Adventure.objects.add_participant(adventure.id, user.id)
        removed = Adventure.objects.remove_participant(adventure.id, user.id)
        self.assertTrue(added, msg=None)
        self.assertTrue(removed, msg=None)

        participant = AdventureParticipant.query.filter_by(
            adventure_id=adventure.id,
            user_id=user.id
        ).first()

        self.assertIsNotNone(participant, msg=None)
        self.assertFalse(participant.is_active(), msg=None)

        removed = Adventure.objects.remove_participant(adventure.id, user.id)
        self.assertFalse(removed, msg=None)
