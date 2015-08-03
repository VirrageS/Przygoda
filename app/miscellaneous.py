# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import wraps
from flask.ext.login import current_user
from flask.ext.babel import gettext
from flask import redirect, url_for, flash, abort, make_response, jsonify, request
from app.users import constants as USER
from app import app, db

from app.users.models import User
from app.adventures.models import Adventure, AdventureParticipant, Coordinate
from random import randint, uniform, sample
from werkzeug import generate_password_hash

def confirmed_email_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if (current_user is None) or (current_user.confirmed is False):
			flash(gettext(u'You have to confirm your email to use this feature'), 'danger')
			return redirect(url_for('simple_page.index'))

		return f(*args, **kwargs)
	return wrapper

def not_login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if current_user.is_authenticated():
			return redirect(url_for('simple_page.index'))

		return f(*args, **kwargs)
	return wrapper

def ssl_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if app.config.get("SSL"):
			if request.is_secure:
				return f(*args, **kwargs)
			else:
				return redirect(request.url.replace("http://", "https://"))

		return f(*args, **kwargs)
	return wrapper

# Usage @rule_required('admin', 'user')
def rule_required(f, *roles):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if str(current_user.role) not in roles:
			return abort(404)

		return f(*args, **kwargs)
	return wrapper

# decorator to filter no-admin users
def admin_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if (not current_user.is_authenticated()) or (current_user.role != USER.ADMIN):
			return abort(404)

		return f(*args, **kwargs)
	return wrapper

# function to add admin to database
def add_admin():
	# add admin
	admin = User.query.filter_by(username="admin").first()
	if admin is None:
		new_admin = User("admin", generate_password_hash("supertajnehaslo"), "email@email.com", social_id=None)
		new_admin.role = USER.ADMIN
		new_admin.confirmed = True
		db.session.add(new_admin)
		db.session.commit()

# decorator to compute time of the fuction
def execution_time(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		time_start = datetime.now()
		result = f(*args, **kwargs)
		time_stop = datetime.now()

		flash('%r (%r, %r) %s sec' % (f.__name__, args, kwargs, str(time_stop-time_start)), 'info')
		return result
	return wrapper

# compute days difference between two dates
def daterange(start_date, end_date):
	for day in range(int((end_date - start_date).days)):
		yield start_date + timedelta(day)

# decorator to filter no-api_key requests to api
def api_key_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if ('key' not in request.args) or (request.args["key"] != app.config["API_KEY"]):
			return make_response(jsonify({'error': 'No authenticated'}), 401)

		return f(*args, **kwargs)
	return wrapper

def get_current_user_id():
	if (current_user is None) or (not current_user.is_authenticated()):
		return None

	return current_user.id


def add_fake_data():
	# add users
	users = [
		{'username': 'tomek', 'email':'tomek@tomek.com', 'password': 't'},
		{'username': 'tomek1', 'email':'tomek1@tomek.com', 'password': 't'},
		{'username': 'tomek2', 'email':'tomek2@tomek.com', 'password': 't'},
		{'username': 'atomek', 'email':'atomek@tomek.com', 'password': 'a'},
		{'username': 'kolega', 'email':'kolega@tomek.com', 'password': 'k'},
		{'username': 'ziomek', 'email':'ziomek@tomek.com', 'password': 'z'},
		{'username': 'ziomek0', 'email':'ziomek0@tomek.com', 'password': 'z'},
		{'username': 'ziomek1', 'email':'ziomek1@tomek.com', 'password': 'z'},
		{'username': 'ziomek2', 'email':'ziomek2@tomek.com', 'password': 'z'},
		{'username': 'ziomek3', 'email':'ziomek3@tomek.com', 'password': 'z'},
		{'username': 'ziomek4', 'email':'ziomek4@tomek.com', 'password': 'z'},
		{'username': 'ziomek5', 'email':'ziomek5@tomek.com', 'password': 'z'},
		{'username': 'ziosfdmek6', 'email':'ziomek6@tomek.com', 'password': 'z'},
		{'username': 'ziosfmek11', 'email':'ziomek111ek6@tomek.com', 'password': 'z'},
		{'username': 'zisdfsdfomek111', 'email':'ziom1ek6@tomek.co1m', 'password': 'z'},
		{'username': 'zi1sdfsfsfomek6', 'email':'zi1om1ek6@tomek.co1m', 'password': 'z'},
		{'username': 'zio1me1k6', 'email':'zio1m1ek6@tome1k.com', 'password': 'z'},
		{'username': 'sfsdfsd', 'email':'ziomek1111ek6@tomek.com1', 'password': 'z'},
		{'username': 'zassdfdfsfiom1ek6', 'email':'zio1mek6@tomek1.com1', 'password': 'z'},
		{'username': 'ziom11ek6', 'email':'zio1mek6@tomek.co1m', 'password': 'z'},
		{'username': 'zio111mek61iomek6', 'email':'zio111mek6@to1mek.com', 'password': 'z'},
		{'username': 'ziom111111ek6', 'email':'zio11mek6@tomek.c1om', 'password': 'z'},
		{'username': 'zsdfasio1mek6', 'email':'zi11111111o1mek6@tomek.com', 'password': 'z'},
		{'username': 'romek', 'email':'romek@romek.com1', 'password': 'r'}
	]

	for user in users:
		# add user
		new_user = User(
			username=user['username'],
			email=user['email'],
			password=generate_password_hash(user['password'])
		)
		db.session.add(new_user)
		db.session.commit()

	# add adventures
	for _ in range(1, 100):
		# add adventure
		creator = randint(1, len(users))
		adventure = Adventure(
			creator_id=creator,
			date=datetime.now() + timedelta(days=randint(0, 10), hours=randint(0, 20)),
			mode=randint(0, 2),
			info='aaaaaa'
		)
		adventure.created_on = datetime.now() + timedelta(days=-randint(0, 3), hours=-randint(0, 23))
		db.session.add(adventure)
		db.session.commit()

		# add creator
		creator_participant = AdventureParticipant(adventure_id=adventure.id, user_id=creator)
		db.session.add(creator_participant)
		db.session.commit()

		# add participants
		available_participants = [number for number in range(1, len(users)) if number != creator]
		random_participants = sample(available_participants, int(randint(0, 10)))

		for participant in random_participants:
			adventure_participant = AdventureParticipant(adventure_id=adventure.id, user_id=participant)
			db.session.add(adventure_participant)
			db.session.commit()


		# add coordinates
		i = 0
		for _ in range(2, 7):
			coordinate = Coordinate(
				adventure_id=adventure.id,
				path_point=i,
				latitude=52.2 + uniform(-0.02, 0.02),
				longitude=21.1 + uniform(-0.02, 0.02)
			)
			db.session.add(coordinate)
			db.session.commit()

			i += 1


def db_init_with_data():
	db.create_all()
	add_admin()
	add_fake_data()
