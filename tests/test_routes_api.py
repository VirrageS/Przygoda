import os
import unittest

from datetime import datetime, timedelta
from config import base_dir
from werkzeug import check_password_hash, generate_password_hash

from flask import Flask, render_template, g
from flask_testing import TestCase

from flask_login import login_user, logout_user, login_required, LoginManager, current_user

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES


class RoutesApiTestCase(TestCase, unittest.TestCase):
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

    def test_api_user_login_route_no_data(self):
        """Ensure that login route requires data"""

        response = self.app.get('/api/v1.0/user/login', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/api/v1.0/user/login?email=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Password not provided"\n}')

        response = self.app.get('/api/v1.0/user/login?password=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Email not provided"\n}')

        response = self.app.get('/api/v1.0/user/login?email=&password=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_api_user_login_route_strange_data(self):
        """Ensure that login route requires normal data"""

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        response = self.app.get('/api/v1.0/user/login?email=sdfw234&password=sdf232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User not found"\n}')

        response = self.app.get('/api/v1.0/user/login?email=23.2&password=232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User not found"\n}')

        response = self.app.get('/api/v1.0/user/login?email=john@example.com&password=234.24', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Password not correct"\n}')

        response = self.app.get('/api/v1.0/user/login?email=-1123&password=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User not found"\n}')

        response = self.app.get('/api/v1.0/user/login?email=john@example.com&password=11231231231231231231231231231231241242142', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Password not correct"\n}')

        response = self.app.get('/api/v1.0/user/login?email=124124124124124124124124124124124&password=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User not found"\n}')


    def test_api_user_login_route_wrong_email(self):
        """Ensure users login does not accept wrong email"""

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        response = self.app.get('/api/v1.0/user/login?email=johner@example.com&password=a', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User not found"\n}')

    def test_api_user_login_route_wrong_password(self):
        """Ensure users login does not accept wrong password"""

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        response = self.app.get('/api/v1.0/user/login?email=john@example.com&password=ab', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Password not correct"\n}')

    def test_api_user_login_route_login(self):
        """Ensure users login actually login the user"""

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        response = self.app.get('/api/v1.0/user/login?email=john@example.com&password=a', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    def test_api_user_register_route_no_data(self):
        """Ensure that register route requires data"""

        response = self.app.get('/api/v1.0/user/register', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/api/v1.0/user/register?email=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Username not provided"\n}')

        response = self.app.get('/api/v1.0/user/register?username=a&email=a', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Password not provided"\n}')

        response = self.app.get('/api/v1.0/user/register?username=a&password=a', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Email not provided"\n}')

        response = self.app.get('/api/v1.0/user/register?username=a&email=b&password=c', follow_redirects=True)
        self.assertEqual(response.data, b'{\n  "error": "Confirm password not provided"\n}')
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/api/v1.0/user/register?username=&email=&password=&confirm=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_api_user_register_route_strange_data(self):
        """Ensure that register route requires normal data"""

        response = self.app.get('/api/v1.0/user/register?username=sdfsdf&email=sdfw234&password=sdf232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Confirm password not provided"\n}')

        response = self.app.get('/api/v1.0/user/register?username=s&email=23.2&password=232&confirm=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Field must be between 4 and 25 characters long."\n}')

        response = self.app.get('/api/v1.0/user/register?username=sasdfasdfasdfasdfasfasdfasdfasdf&email=john@example.com&password=234.24&confirm=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Field must be between 4 and 25 characters long."\n}')

        response = self.app.get('/api/v1.0/user/register?username=sdfsdf&email=-1123&password=1&confirm=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Invalid email address."\n}')

        response = self.app.get('/api/v1.0/user/register?username=sdfsdf&email=john@example.com&password=1&confirm=12', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Passwords must match."\n}')


    def test_api_user_register_route_user_exists_with_username(self):
        """Ensure users register does not allow to register when someone exists with username"""

        u = User(username='tomek', password=generate_password_hash('a'), email='tomeked@tomek.com')
        db.session.add(u)
        db.session.commit()

        response = self.app.get('/api/v1.0/user/register?username=tomek&email=tomeaaked@tomek.com&password=1&confirm=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Username is already in use."\n}')


    def test_api_user_register_route_user_exists_with_email(self):
        """Ensure users register does not allow to register when someone exists with email"""

        u = User(username='tomeczek', password=generate_password_hash('a'), email='tomek@tomek.com')
        db.session.add(u)
        db.session.commit()

        response = self.app.get('/api/v1.0/user/register?username=tomek&email=tomek@tomek.com&password=1&confirm=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Email is already in use."\n}')


    def test_api_user_register_route_register(self):
        """Ensure users register actually create the user"""

        response = self.app.get('/api/v1.0/user/register?username=tomek&email=tomek@tomek.com&password=1&confirm=1', follow_redirects=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, b'{\n  "success": "User has been created"\n}')

        u = User.query.filter_by(username='tomek').first()
        self.assertTrue(u is not None)
        self.assertTrue(u.email == 'tomek@tomek.com')
        self.assertTrue(check_password_hash(u.password, '1'))






    def test_api_user_get_adventures_route_no_data(self):
        """Ensure that user get adventures route requires data"""

        response = self.app.get('/api/v1.0/user/get/adventures', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User id not provided"\n}')

    def test_api_user_get_adventures_route_strange_data(self):
        """Ensure that user get adventures route requires normal data"""

        response = self.app.get('/api/v1.0/user/get/adventures?user_id=sdfw234', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/user/get/adventures?user_id=23.2', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/user/get/adventures?user_id=-1123', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/user/get/adventures?user_id=124124124124124124124124124124124', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

    def test_api_user_get_adventures_route_user_no_exists(self):
        """Ensure that user get adventures route requires existing"""

        response = self.app.get('/api/v1.0/user/get/adventures?user_id=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User does not exists"\n}')

    def test_api_user_get_adventures_route_get(self):
        """Ensure that user get adventures route returns good format adventure"""

        # add adventure to database
        adventure_first = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(adventure_first)
        db.session.commit()

        # add user to database
        creator = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(creator)
        db.session.commit()

        # add user to adventure participants
        ap11 = AdventureParticipant(user_id=1, adventure_id=1)
        db.session.add(ap11)
        db.session.commit()

        ap12 = AdventureParticipant(user_id=2, adventure_id=1)
        db.session.add(ap12)
        db.session.commit()

        # add some coordinates to database
        c = Coordinate(adventure_id=1, path_point=1, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        c = Coordinate(adventure_id=1, path_point=2, latitude=51.24324242, longitude=51.24324242)
        db.session.add(c)
        db.session.commit()

        # SECOND ADVENTURE

        # add adventure to database
        adventure_second = Adventure(creator_id=2, date=datetime.now() + timedelta(minutes=11), mode=ADVENTURES.AMATEURISH, info='Some info sadfstoday')
        db.session.add(adventure_second)
        db.session.commit()

        # add user to database
        creator_dummy = User(username='johner', password=generate_password_hash('a'), email='johner@example.com')
        db.session.add(creator_dummy)
        db.session.commit()

        # add user to adventure participants
        ap21 = AdventureParticipant(user_id=1, adventure_id=2)
        db.session.add(ap21)
        db.session.commit()

        ap22 = AdventureParticipant(user_id=2, adventure_id=2)
        db.session.add(ap22)
        db.session.commit()

        # add some coordinates to database
        c = Coordinate(adventure_id=2, path_point=1, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        c = Coordinate(adventure_id=2, path_point=2, latitude=52.24324242, longitude=52.24324242)
        db.session.add(c)
        db.session.commit()

        response = self.app.get('/api/v1.0/user/get/adventures?user_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.replace(b", ", b","), b'\
{\n\
  "created": {\n\
    "' + str(adventure_first.id).encode('utf-8') + b'": {\n\
      "coordinates": {\n\
        "1": {\n\
          "latitude": 50.24324242,\n\
          "longitude": 50.24324242\n\
        },\n\
        "2": {\n\
          "latitude": 51.24324242,\n\
          "longitude": 51.24324242\n\
        }\n\
      },\n\
      "creator_id": ' + str(creator.id).encode('utf-8') + b',\n\
      "creator_username": "' + str(creator.username).encode('utf-8') + b'",\n\
      "date": ' + str(int(adventure_first.date.strftime("%s"))).encode('utf-8') + b',\n\
      "id": ' + str(adventure_first.id).encode('utf-8') + b',\n\
      "info": "' + str(adventure_first.info).encode('utf-8') + b'",\n\
      "joined": 2,\n\
      "mode": ' + str(adventure_first.mode).encode('utf-8') + b',\n\
      "mode_name": "' + str(ADVENTURES.MODES[adventure_first.mode]).encode('utf-8') + b'",\n\
      "participants": {\n\
        "' + str(creator.id).encode('utf-8') + b'": {\n\
          "id": ' + str(creator.id).encode('utf-8') + b',\n\
          "joined_on": ' + str(ap11.joined_on.strftime("%s")).encode('utf-8') + b',\n\
          "username": "' + str(creator.username).encode('utf-8') + b'"\n\
        },\n\
        "' + str(creator_dummy.id).encode('utf-8') + b'": {\n\
          "id": ' + str(creator_dummy.id).encode('utf-8') + b',\n\
          "joined_on": ' + str(ap12.joined_on.strftime("%s")).encode('utf-8') + b',\n\
          "username": "' + str(creator_dummy.username).encode('utf-8') + b'"\n\
        }\n\
      },\n\
      "static_image_url": "https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off&style=feature:road|element:labels.text.fill|color:0x959595&style=feature:poi|element:all|visibility:off&style=feature:administrative|element:all|visiblity:off&path=color:0x0000ff|weight:5|50.24324242,50.24324242|51.24324242,51.24324242"\n\
    }\n\
  },\n\
  "joined": {\n\
    "' + str(adventure_second.id).encode('utf-8') + b'": {\n\
      "coordinates": {\n\
        "1": {\n\
          "latitude": 50.24324242,\n\
          "longitude": 50.24324242\n\
        },\n\
        "2": {\n\
          "latitude": 52.24324242,\n\
          "longitude": 52.24324242\n\
        }\n\
      },\n\
      "creator_id": ' + str(creator_dummy.id).encode('utf-8') + b',\n\
      "creator_username": "' + str(creator_dummy.username).encode('utf-8') + b'",\n\
      "date": ' + str(int(adventure_second.date.strftime("%s"))).encode('utf-8') + b',\n\
      "id": ' + str(adventure_second.id).encode('utf-8') + b',\n\
      "info": "' + str(adventure_second.info).encode('utf-8') + b'",\n\
      "joined": 2,\n\
      "mode": ' + str(adventure_second.mode).encode('utf-8') + b',\n\
      "mode_name": "' + str(ADVENTURES.MODES[adventure_second.mode]).encode('utf-8') + b'",\n\
      "participants": {\n\
        "' + str(creator.id).encode('utf-8') + b'": {\n\
          "id": ' + str(creator.id).encode('utf-8') + b',\n\
          "joined_on": ' + str(ap21.joined_on.strftime("%s")).encode('utf-8') + b',\n\
          "username": "' + str(creator.username).encode('utf-8') + b'"\n\
        },\n\
        "' + str(creator_dummy.id).encode('utf-8') + b'": {\n\
          "id": ' + str(creator_dummy.id).encode('utf-8') + b',\n\
          "joined_on": ' + str(ap22.joined_on.strftime("%s")).encode('utf-8') + b',\n\
          "username": "' + str(creator_dummy.username).encode('utf-8') + b'"\n\
        }\n\
      },\n\
      "static_image_url": "https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off&style=feature:road|element:labels.text.fill|color:0x959595&style=feature:poi|element:all|visibility:off&style=feature:administrative|element:all|visiblity:off&path=color:0x0000ff|weight:5|50.24324242,50.24324242|52.24324242,52.24324242"\n\
    }\n\
  }\n\
}')




    ###
    ### ADVENTURES
    ###

    def test_api_adventure_get_route_no_data(self):
        """Ensure that get route requires data"""

        response = self.app.get('/api/v1.0/adventure/get', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        response = self.app.get('/api/v1.0/adventure/get/', follow_redirects=True)
        self.assertEqual(response.status_code, 404)


    def test_api_adventure_get_route_strange_data(self):
        """Ensure that get route requires normal data"""

        response = self.app.get('/api/v1.0/adventure/get/234230423-049203-49230-492340-2394-34', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        response = self.app.get('/api/v1.0/adventure/get/1.0', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        response = self.app.get('/api/v1.0/adventure/get/-1', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        response = self.app.get('/api/v1.0/adventure/get/4923492384920348230942834923842903423094', follow_redirects=True)
        self.assertEqual(response.data, b'{\n  "error": "Adventure id is invalid"\n}')
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/api/v1.0/adventure/get/a', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        response = self.app.get('/api/v1.0/adventure/get/.1', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_api_adventure_get_route_no_adventure(self):
        """Ensure that get adventure require existing adventure"""

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/get/1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')

    def test_api_adventure_get_route_adventure_no_active(self):
        """Ensure that get adventure require active adventure"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=-10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/get/1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')


    def test_api_adventure_get_route_no_user(self):
        """Ensure that get adventure require existing user"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        response = self.app.get('/api/v1.0/adventure/get/1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Creator of adventure does not exists"\n}')


    def test_api_adventure_get_route_get(self):
        """Ensure that get adventure returns good format adventure"""

        # add adventure to database
        adventure = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(adventure)
        db.session.commit()

        # add user to database
        creator = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(creator)
        db.session.commit()

        self.assertEqual(creator.id, 1)

        # add user to database
        u = User(username='johner', password=generate_password_hash('a'), email='johner@example.com')
        db.session.add(u)
        db.session.commit()

        # add user to adventure participants
        ap1 = AdventureParticipant(user_id=1, adventure_id=1)
        db.session.add(ap1)
        db.session.commit()

        ap2 = AdventureParticipant(user_id=2, adventure_id=1)
        db.session.add(ap2)
        db.session.commit()

        # add some coordinates to database
        c = Coordinate(adventure_id=1, path_point=1, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        c = Coordinate(adventure_id=1, path_point=2, latitude=51.24324242, longitude=51.24324242)
        db.session.add(c)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/get/1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.replace(b", ", b","), b'\
{\n\
  "coordinates": {\n\
    "1": {\n\
      "latitude": 50.24324242,\n\
      "longitude": 50.24324242\n\
    },\n\
    "2": {\n\
      "latitude": 51.24324242,\n\
      "longitude": 51.24324242\n\
    }\n\
  },\n\
  "creator_id": ' + str(creator.id).encode('utf-8') + b',\n\
  "creator_username": "' + str(creator.username).encode('utf-8') + b'",\n\
  "date": ' + str(int(adventure.date.strftime("%s"))).encode('utf-8') + b',\n\
  "id": ' + str(adventure.id).encode('utf-8') + b',\n\
  "info": "' + str(adventure.info).encode('utf-8') + b'",\n\
  "joined": 2,\n\
  "mode": ' + str(adventure.mode).encode('utf-8') + b',\n\
  "mode_name": "' + str(ADVENTURES.MODES[adventure.mode]).encode('utf-8') + b'",\n\
  "participants": {\n\
    "' + str(creator.id).encode('utf-8') + b'": {\n\
      "id": ' + str(creator.id).encode('utf-8') + b',\n\
      "joined_on": ' + str(ap1.joined_on.strftime("%s")).encode('utf-8') + b',\n\
      "username": "' + str(creator.username).encode('utf-8') + b'"\n\
    },\n\
    "' + str(u.id).encode('utf-8') + b'": {\n\
      "id": ' + str(u.id).encode('utf-8') + b',\n\
      "joined_on": ' + str(ap2.joined_on.strftime("%s")).encode('utf-8') + b',\n\
      "username": "' + str(u.username).encode('utf-8') + b'"\n\
    }\n\
  },\n\
  "static_image_url": "https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off&style=feature:road|element:labels.text.fill|color:0x959595&style=feature:poi|element:all|visibility:off&style=feature:administrative|element:all|visiblity:off&path=color:0x0000ff|weight:5|50.24324242,50.24324242|51.24324242,51.24324242"\n\
}')


    def test_api_adventure_get_all_route_no_data(self):
        """Ensure that get all route requires data"""

        response = self.app.get('/api/v1.0/adventure/get/all', follow_redirects=False)
        self.assertEqual(response.status_code, 301)

        response = self.app.get('/api/v1.0/adventure/get/all/a', follow_redirects=True)
        self.assertEqual(response.status_code, 404)


    def test_api_adventure_get_all_route_get(self):
        """Ensure that get adventure returns good format adventure"""

        # add adventure to database
        adventure = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(adventure)
        db.session.commit()

        # add user to database
        creator = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(creator)
        db.session.commit()

        # add user to database
        u = User(username='johner', password=generate_password_hash('a'), email='johner@example.com')
        db.session.add(u)
        db.session.commit()

        # add user to adventure participants
        ap1 = AdventureParticipant(user_id=1, adventure_id=1)
        db.session.add(ap1)
        db.session.commit()

        ap2 = AdventureParticipant(user_id=2, adventure_id=1)
        db.session.add(ap2)
        db.session.commit()

        # add some coordinates to database
        c = Coordinate(adventure_id=1, path_point=1, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        c = Coordinate(adventure_id=1, path_point=2, latitude=51.24324242, longitude=51.24324242)
        db.session.add(c)
        db.session.commit()

        # SECOND ADVENTURE

        # add adventure to database
        adventure2 = Adventure(creator_id=3, date=datetime.now() + timedelta(minutes=11), mode=ADVENTURES.AMATEURISH, info='Some info sadfstoday')
        db.session.add(adventure2)
        db.session.commit()

        # add user to database
        creator2 = User(username='johny', password=generate_password_hash('a'), email='johny@example.com')
        db.session.add(creator2)
        db.session.commit()

        # add user to database
        user2 = User(username='johnery', password=generate_password_hash('a'), email='johnery@example.com')
        db.session.add(user2)
        db.session.commit()

        # add user to adventure participants
        ap21 = AdventureParticipant(user_id=3, adventure_id=2)
        db.session.add(ap21)
        db.session.commit()

        ap22 = AdventureParticipant(user_id=4, adventure_id=2)
        db.session.add(ap22)
        db.session.commit()

        # add some coordinates to database
        c = Coordinate(adventure_id=2, path_point=1, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        c = Coordinate(adventure_id=2, path_point=2, latitude=52.24324242, longitude=52.24324242)
        db.session.add(c)
        db.session.commit()


        response = self.app.get('/api/v1.0/adventure/get/all/', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.replace(b", ", b","), b'\
{\n\
  "' + str(adventure.id).encode('utf-8') + b'": {\n\
    "coordinates": {\n\
      "1": {\n\
        "latitude": 50.24324242,\n\
        "longitude": 50.24324242\n\
      },\n\
      "2": {\n\
        "latitude": 51.24324242,\n\
        "longitude": 51.24324242\n\
      }\n\
    },\n\
    "creator_id": ' + str(creator.id).encode('utf-8') + b',\n\
    "creator_username": "' + str(creator.username).encode('utf-8') + b'",\n\
    "date": ' + str(int(adventure.date.strftime("%s"))).encode('utf-8') + b',\n\
    "id": ' + str(adventure.id).encode('utf-8') + b',\n\
    "info": "' + str(adventure.info).encode('utf-8') + b'",\n\
    "joined": 2,\n\
    "mode": ' + str(adventure.mode).encode('utf-8') + b',\n\
    "mode_name": "' + str(ADVENTURES.MODES[adventure.mode]).encode('utf-8') + b'",\n\
    "participants": {\n\
      "' + str(creator.id).encode('utf-8') + b'": {\n\
        "id": ' + str(creator.id).encode('utf-8') + b',\n\
        "joined_on": ' + str(ap1.joined_on.strftime("%s")).encode('utf-8') + b',\n\
        "username": "' + str(creator.username).encode('utf-8') + b'"\n\
      },\n\
      "' + str(u.id).encode('utf-8') + b'": {\n\
        "id": ' + str(u.id).encode('utf-8') + b',\n\
        "joined_on": ' + str(ap2.joined_on.strftime("%s")).encode('utf-8') + b',\n\
        "username": "' + str(u.username).encode('utf-8') + b'"\n\
      }\n\
    },\n\
    "static_image_url": "https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off&style=feature:road|element:labels.text.fill|color:0x959595&style=feature:poi|element:all|visibility:off&style=feature:administrative|element:all|visiblity:off&path=color:0x0000ff|weight:5|50.24324242,50.24324242|51.24324242,51.24324242"\n\
  },\n\
  "' + str(adventure2.id).encode('utf-8') + b'": {\n\
    "coordinates": {\n\
      "1": {\n\
        "latitude": 50.24324242,\n\
        "longitude": 50.24324242\n\
      },\n\
      "2": {\n\
        "latitude": 52.24324242,\n\
        "longitude": 52.24324242\n\
      }\n\
    },\n\
    "creator_id": ' + str(creator2.id).encode('utf-8') + b',\n\
    "creator_username": "' + str(creator2.username).encode('utf-8') + b'",\n\
    "date": ' + str(int(adventure2.date.strftime("%s"))).encode('utf-8') + b',\n\
    "id": ' + str(adventure2.id).encode('utf-8') + b',\n\
    "info": "' + str(adventure2.info).encode('utf-8') + b'",\n\
    "joined": 2,\n\
    "mode": ' + str(adventure2.mode).encode('utf-8') + b',\n\
    "mode_name": "' + str(ADVENTURES.MODES[adventure2.mode]).encode('utf-8') + b'",\n\
    "participants": {\n\
      "' + str(creator2.id).encode('utf-8') + b'": {\n\
        "id": ' + str(creator2.id).encode('utf-8') + b',\n\
        "joined_on": ' + str(ap21.joined_on.strftime("%s")).encode('utf-8') + b',\n\
        "username": "' + str(creator2.username).encode('utf-8') + b'"\n\
      },\n\
      "' + str(user2.id).encode('utf-8') + b'": {\n\
        "id": ' + str(user2.id).encode('utf-8') + b',\n\
        "joined_on": ' + str(ap22.joined_on.strftime("%s")).encode('utf-8') + b',\n\
        "username": "' + str(user2.username).encode('utf-8') + b'"\n\
      }\n\
    },\n\
    "static_image_url": "https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off&style=feature:road|element:labels.text.fill|color:0x959595&style=feature:poi|element:all|visibility:off&style=feature:administrative|element:all|visiblity:off&path=color:0x0000ff|weight:5|50.24324242,50.24324242|52.24324242,52.24324242"\n\
  }\n\
}')



    def test_api_adventure_join_route_no_data(self):
        """Ensure that join route requires data"""

        response = self.app.get('/api/v1.0/adventure/join', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/api/v1.0/adventure/join?user_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure id not provided"\n}')

        response = self.app.get('/api/v1.0/adventure/join?adventure_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User id not provided"\n}')

        response = self.app.get('/api/v1.0/adventure/join?user_id=&adventure_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_api_adventure_join_route_strange_data(self):
        """Ensure that join route requires normal data"""

        response = self.app.get('/api/v1.0/adventure/join?user_id=sdfw234&adventure_id=sdf232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/join?user_id=23.2&adventure_id=232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/join?user_id=234&adventure_id=234.24', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/join?user_id=-1123&adventure_id=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=11231231231231231231231231231231241242142', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/join?user_id=124124124124124124124124124124124&adventure_id=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

    def test_api_adventure_join_route_no_adventure(self):
        """Ensure that join adventure require existing adventure"""

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')

    def test_api_adventure_join_route_adventure_no_active(self):
        """Ensure that join adventure require active adventure"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=-10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')


    def test_api_adventure_join_route_no_creator(self):
        """Ensure that join adventure require existing creator"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User does not exists"\n}')


    def test_api_adventure_join_route_user_already_joined(self):
        """Ensure that join adventure does not allow to join again"""

        response = self.app.get('/api/v1.0/adventure/join/1', follow_redirects=True)

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        self.assertTrue(a.id == 1)

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # add user to adventure participants
        ap = AdventureParticipant(user_id=1, adventure_id=1)
        db.session.add(ap)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User has joined this adventure before"\n}')


    def test_api_adventure_join_route_join(self):
        """Ensure that join adventure create adventure participant"""

        # add adventure to database
        a = Adventure(creator_id=2, date=datetime.now() + timedelta(minutes=9), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{\n  "success": "User has joined the adventure"\n}')

        ap = AdventureParticipant.query.filter_by(user_id=1, adventure_id=1).first()
        self.assertTrue(ap is not None)
        self.assertTrue(ap.is_active())


    def test_api_adventure_join_route_join_after_leaving(self):
        """Ensure that join adventure updating adventure participant after joining"""

        # add adventure to database
        a = Adventure(creator_id=2, date=datetime.now() + timedelta(minutes=9), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # trigger user joining
        self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=1', follow_redirects=True)

        ap = AdventureParticipant.query.filter_by(user_id=1, adventure_id=1).first()
        self.assertTrue(ap is not None)
        self.assertTrue(ap.is_active())

        # trigger user leaving
        self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        ap = AdventureParticipant.query.filter_by(user_id=1, adventure_id=1).first()
        self.assertTrue(ap is not None)
        self.assertTrue(not ap.is_active())

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/join?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{\n  "success": "User has joined the adventure"\n}')

        ap = AdventureParticipant.query.filter_by(user_id=1, adventure_id=1).first()
        self.assertTrue(ap is not None)
        self.assertTrue(ap.is_active())


    def test_api_adventure_leave_route_no_data(self):
        """Ensure that leave route requires data"""

        response = self.app.get('/api/v1.0/adventure/leave', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/api/v1.0/adventure/leave?user_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure id not provided"\n}')

        response = self.app.get('/api/v1.0/adventure/leave?adventure_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User id not provided"\n}')

        response = self.app.get('/api/v1.0/adventure/leave?user_id=&adventure_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_api_adventure_leave_route_strange_data(self):
        """Ensure that leave route requires normal data"""

        response = self.app.get('/api/v1.0/adventure/leave?user_id=sdfw234&adventure_id=sdf232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/leave?user_id=23.2&adventure_id=232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/leave?user_id=234&adventure_id=234.24', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/leave?user_id=-1123&adventure_id=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=11231231231231231231231231231231241242142', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/leave?user_id=124124124124124124124124124124124&adventure_id=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')


    def test_api_adventure_leave_route_no_adventure(self):
        """Ensure that leave adventure require existing adventure"""

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')


    def test_api_adventure_leave_route_adventure_no_active(self):
        """Ensure that leave adventure require active adventure"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=-10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')


    def test_api_adventure_leave_route_no_user(self):
        """Ensure that leave adventure require existing user"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User does not exists"\n}')


    def test_api_adventure_leave_route_creator(self):
        """Ensure that leave adventure do not allow leaving for creator of the adventure"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User cannot leave this adventure"\n}')


    def test_api_adventure_leave_route_no_joined(self):
        """Ensure that leave adventure do not allow leaving for someone who does not joined to adventure"""

        # add adventure to database
        a = Adventure(creator_id=2, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User has not joined this adventure"\n}')


    def test_api_adventure_leave_route_adventure_no_active(self):
        """Ensure that leave adventure do not allow leaving if the adventure is not active"""

        # add adventure to database
        a = Adventure(creator_id=2, date=datetime.now(), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # add user to adventure participants
        ap = AdventureParticipant(user_id=1, adventure_id=1)
        db.session.add(ap)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')

        # check if user was removed from adventure participants
        ap = AdventureParticipant.query.filter_by(adventure_id=1).first()
        self.assertTrue(ap is not None)
        self.assertTrue(ap.is_active())


    def test_api_adventure_leave_route_leave(self):
        """Ensure that leave adventure actually allows to leave the adventure"""

        # add adventure to database
        a = Adventure(creator_id=2, date=datetime.now() + timedelta(minutes=9), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # add user to adventure participants
        ap = AdventureParticipant(user_id=1, adventure_id=1)
        db.session.add(ap)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/leave?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{\n  "success": "User has left the adventure"\n}')

        # check if user was removed from adventure participants
        ap = AdventureParticipant.query.filter_by(adventure_id=1).first()
        self.assertTrue(ap is not None)
        self.assertTrue(not ap.is_active())


    def test_api_adventure_delete_route_no_data(self):
        """Ensure that delete route requires data"""

        response = self.app.get('/api/v1.0/adventure/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.get('/api/v1.0/adventure/delete?user_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure id not provided"\n}')

        response = self.app.get('/api/v1.0/adventure/delete?adventure_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User id not provided"\n}')

        response = self.app.get('/api/v1.0/adventure/delete?user_id=&adventure_id=', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_api_adventure_delete_route_strange_data(self):
        """Ensure that delete route requires normal data"""

        response = self.app.get('/api/v1.0/adventure/delete?user_id=sdfw234&adventure_id=sdf232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/delete?user_id=23.2&adventure_id=232', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/delete?user_id=234&adventure_id=234.24', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/delete?user_id=-1123&adventure_id=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/delete?user_id=1&adventure_id=11231231231231231231231231231231241242142', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')

        response = self.app.get('/api/v1.0/adventure/delete?user_id=124124124124124124124124124124124&adventure_id=1', follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Input error"\n}')


    def test_api_adventure_delete_route_no_adventure(self):
        """Ensure that delete adventure require existing adventure"""

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/delete?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')


    def test_api_adventure_delete_route_adventure_no_active(self):
        """Ensure that leave adventure require active adventure"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=-10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/delete?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')


    def test_api_adventure_delete_route_no_user(self):
        """Ensure that delete adventure require existing user"""

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/delete?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User does not exists"\n}')


    def test_api_adventure_delete_route_no_creator(self):
        """Ensure that delete adventure requires creator to be logged"""

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # add adventure to database
        a = Adventure(creator_id=2, date=datetime.now() + timedelta(minutes=10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/delete?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "User is not creator of adventure"\n}')

    def test_api_adventure_delete_route_adventure_no_active(self):
        """Ensure that delete adventure requires for adventure to be active"""

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=-10), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add adventure participants to database
        ap = AdventureParticipant(adventure_id=1, user_id=1)
        db.session.add(ap)
        db.session.commit()

        # add some coordinates to database
        c = Coordinate(adventure_id=1, path_point=1, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        # trigger user joining
        response = self.app.get('/api/v1.0/adventure/delete?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{\n  "error": "Adventure does not exists"\n}')

        a = Adventure.query.filter_by(id=1).first()
        ap = AdventureParticipant.query.filter_by(adventure_id=1).first()
        c = Coordinate.query.filter_by(adventure_id=1).first()
        self.assertTrue(a is not None)
        self.assertTrue(a.is_active() is False)
        self.assertTrue(ap is not None)
        self.assertTrue(c is not None)


    def test_api_adventure_delete_route_delete(self):
        """Ensure that delete adventure delete all the stuff"""

        # add user to database
        u = User(username='john', password=generate_password_hash('a'), email='john@example.com')
        db.session.add(u)
        db.session.commit()

        # add adventure to database
        a = Adventure(creator_id=1, date=datetime.now() + timedelta(minutes=9), mode=ADVENTURES.RECREATIONAL, info='Some info today')
        db.session.add(a)
        db.session.commit()

        # add adventure participants to database
        ap = AdventureParticipant(adventure_id=1, user_id=2)
        db.session.add(ap)
        db.session.commit()

        ap = AdventureParticipant(adventure_id=1, user_id=3)
        db.session.add(ap)
        db.session.commit()

        # add some coordinates to database
        c = Coordinate(adventure_id=1, path_point=1, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        c = Coordinate(adventure_id=1, path_point=2, latitude=50.24324242, longitude=50.24324242)
        db.session.add(c)
        db.session.commit()

        # trigger adventure deleting
        response = self.app.get('/api/v1.0/adventure/delete?user_id=1&adventure_id=1', follow_redirects=True)

        # check proper response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{\n  "success": "Adventure has been deleted"\n}')

        a = Adventure.query.filter_by(id=1).first()
        ap = AdventureParticipant.query.filter_by(adventure_id=1).first()
        c = Coordinate.query.filter_by(adventure_id=1).first()
        self.assertTrue(a is not None)
        self.assertTrue(a.is_active() is False)
        self.assertTrue(ap is not None)
        self.assertTrue(c is not None)
