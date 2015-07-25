# -*- coding: utf-8 -*-

import time
from datetime import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response, jsonify, json
from flask.ext.login import current_user, login_user, logout_user, login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import app, db
from app.users.models import User
from app.users.forms import RegisterForm, LoginForm
from app.adventures.models import Adventure, AdventureParticipant, Coordinate

mod = Blueprint('api', __name__, url_prefix='/api/v1.0')

# check for slow quieries
@mod.after_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= app.config['DATABASE_QUERY_TIMEOUT']:
			app.logger.warning(
				"SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
				(query.statement, query.parameters, query.duration, query.context)
			)
	return response

# User login
@mod.route('/user/login', methods=['GET'])
def login():
	if 'email' not in request.args:
		return make_response(jsonify({'error': 'Email not provided'}), 400)

	if 'password' not in request.args:
		return make_response(jsonify({'error': 'Password not provided'}), 400)

	u = User.query.filter_by(email=request.args['email']).first()
	if u is None:
		return make_response(jsonify({'error': 'User not found'}), 400)

	if not check_password_hash(u.password, request.args['password']):
		return make_response(jsonify({'error': 'Password not correct'}), 400)

	response_user = {
		'id': u.id,
		'social_id': u.social_id,
		'username': u.username,
		'email': u.email,
		'registered_on': int(u.registered_on.strftime('%s'))
	}

	# curl -i http://127.0.0.1:5000/api/v1.0/login?username=tomek\&password=t

	return jsonify(response_user)

# User register
@mod.route('/user/register', methods=['GET'])
def register():
	if ('username' not in request.args) or (request.args['username'] == ''):
		return make_response(jsonify({'error': 'Username not provided'}), 400)

	if ('email' not in request.args) or (request.args['email'] == ''):
		return make_response(jsonify({'error': 'Email not provided'}), 400)

	if ('password' not in request.args) or (request.args['password'] == ''):
		return make_response(jsonify({'error': 'Password not provided'}), 400)

	if ('confirm' not in request.args) or (request.args['confirm'] == ''):
		return make_response(jsonify({'error': 'Confirm password not provided'}), 400)

	form = RegisterForm(request.args)
	form.csrf_enabled = False
	if not form.validate():
		errors = []
		errors.append(form.username.errors)
		errors.append(form.email.errors)
		errors.append(form.password.errors)
		errors.append(form.confirm.errors)
		errors = [item for sublist in errors for item in sublist]

		return make_response(jsonify({'error': errors[0]}), 400)

	u = User(username=request.args['username'], email=request.args['email'], password=generate_password_hash(request.args['password']))
	db.session.add(u)
	db.session.commit()
	return make_response(jsonify({'success': 'User has been created'}), 201)


# Adventure get
@mod.route('/adventure/get/<int:adventure_id>', methods=['GET'])
def get_adventure(adventure_id):
	if adventure_id >= 9223372036854775807:
		return make_response(jsonify({'error': 'Adventure id is too large'}), 400)

	a = Adventure.query.filter_by(id=adventure_id).first()
	if (a is None) or (not a.is_active()):
		return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

	# check if creator of the adventure exists
	u = User.query.filter_by(id=a.creator_id).first()
	if u is None:
		return make_response(jsonify({'error': 'Adventure\'s creator does not exists'}), 400)

	# get joined participants
	final_participants = []
	participants = AdventureParticipant.query.filter_by(adventure_id=a.id).all()
	participants = list(filter(lambda ap: ap.is_active(), participants))

	for participant in participants:
		user = User.query.filter_by(id=participant.user_id).first()

		if user is not None:
			final_participants.append(user)

	response_adventure = {
		'id': a.id,
		'creator_id': a.creator_id,
		'date': int(a.date.strftime('%s')),
		'mode': a.mode,
		'info': a.info,
		'joined': len(final_participants)
	}

	return jsonify(response_adventure)

@mod.route('/adventure/get/all/')
def get_all_adventures():
	final_adventures = {}

	# get all adventures
	adventures = Adventure.query.order_by(Adventure.date.asc()).all()

	# filter only active adventures
	adventures = list(filter(lambda a: a.is_active(), adventures))

	for adventure in adventures:
		# get creator and check if exists
		creator = User.query.filter_by(id=adventure.creator_id).first()
		if creator is None:
			continue

		# get joined participants
		final_participants = {}
		participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
		participants = list(filter(lambda ap: ap.is_active(), participants))

		for participant in participants:
			user = User.query.filter_by(id=participant.user_id).first()

			if user is not None:
				final_participants[user.id] = {
					'id': user.id,
					'username': user.username,
					'joined_on': int(participant.joined_on.strftime('%s'))
				}

		# get static image url
		static_image_url = 'https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off&style=feature:road|element:labels.text.fill|color:0x959595&style=feature:poi|element:all|visibility:off&style=feature:administrative|element:all|visiblity:off&path=color:0x0000ff|weight:5'

		# get all coordinates
		final_coordinates = {}
		coordinates = Coordinate.query.filter_by(adventure_id=adventure.id).all()
		for coordinate in coordinates:
			final_coordinates[coordinate.path_point] = {
				'latitude': coordinate.latitude,
				'longitude': coordinate.longitude
			}

			static_image_url += '|' + str(coordinate.latitude) + ',' + str(coordinate.longitude)

		# add everything
		final_adventures[adventure.id] = {
			'id': adventure.id,
			'creator_id': creator.id,
			'creator_name': creator.username,
			'date': int(adventure.date.strftime('%s')),
			'mode': adventure.mode,
			'info': adventure.info,
			'joined': len(final_participants),
			'participants': final_participants,
			'coordinates': final_coordinates,
			'static_image_url': static_image_url
		}

	return jsonify(final_adventures)


@mod.route('/adventure/leave', methods=['GET'])
def leave_adventure():
	# check if data is provided
	if 'user_id' not in request.args:
		return make_response(jsonify({'error': 'User id not provided'}), 400)

	if 'adventure_id' not in request.args:
		return make_response(jsonify({'error': 'Adventure id not provided'}), 400)

	# check if there is no input error
	user_id = None
	adventure_id = None
	try:
		user_id = int(request.args['user_id'])
		adventure_id = int(request.args['adventure_id'])
	except:
		return make_response(jsonify({'error': 'Input error'}), 400)

	if (user_id >= 9223372036854775807) or (user_id < 0) or (adventure_id >= 9223372036854775807) or (adventure_id < 0):
		return make_response(jsonify({'error': 'Input error'}), 400)

	# check if adventure exists
	a = Adventure.query.filter_by(id=adventure_id).first()
	if (a is None) or (not a.is_active()):
		return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

	u = User.query.filter_by(id=user_id).first()
	if u is None:
		return make_response(jsonify({'error': 'User does not exists'}), 400)

	# check if creator_id match with user_id
	if a.creator_id == user_id:
		return make_response(jsonify({'error': 'User cannot leave this adventure'}), 400)

	# get participant
	participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=user_id).first()

	# check if user joined adventure
	if (participant is None) or (not participant.is_active()):
		return make_response(jsonify({'error': 'User has not joined this adventure'}), 400)

	# delete user from adventure participants from database
	participant.left_on = datetime.now()
	db.session.commit()
	return make_response(jsonify({'success': 'User has left the adventure'}), 200)

@mod.route('/adventure/join', methods=['GET'])
def join_adventure():
	# check if data is provided
	if 'user_id' not in request.args:
		return make_response(jsonify({'error': 'User id not provided'}), 400)

	if 'adventure_id' not in request.args:
		return make_response(jsonify({'error': 'Adventure id not provided'}), 400)

	# check if there is no input error
	user_id = None
	adventure_id = None
	try:
		user_id = int(request.args['user_id'])
		adventure_id = int(request.args['adventure_id'])
	except:
		return make_response(jsonify({'error': 'Input error'}), 400)

	if (user_id >= 9223372036854775807) or (user_id < 0) or (adventure_id >= 9223372036854775807) or (adventure_id < 0):
		return make_response(jsonify({'error': 'Input error'}), 400)

	# check if adventure exists
	a = Adventure.query.filter_by(id=adventure_id).first()
	if (a is None) or (not a.is_active()):
		return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

	u = User.query.filter_by(id=user_id).first()
	if u is None:
		return make_response(jsonify({'error': 'User does not exists'}), 400)

	# get participant
	participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=user_id).first()

	# check if user joining adventure for the first time
	if participant is None:
		# add user to adventure participants to database
		participant = AdventureParticipant(adventure_id=adventure_id, user_id=user_id)
		db.session.add(participant)
		db.session.commit()
		return make_response(jsonify({'success': 'User has joined the adventure'}), 200)

	# check if user is rejoining
	if participant.is_active():
		return make_response(jsonify({'error': 'User has joined this adventure before'}), 400)

	# join user again
	participant.left_on = None
	participant.joined_on = datetime.now()
	db.session.add(participant)
	db.session.commit()

	# make response
	return make_response(jsonify({'success': 'User has joined the adventure'}), 200)

@mod.route('/adventure/delete', methods=['GET'])
def delete_adventure():
	# check if data is provided
	if 'user_id' not in request.args:
		return make_response(jsonify({'error': 'User id not provided'}), 400)

	if 'adventure_id' not in request.args:
		return make_response(jsonify({'error': 'Adventure id not provided'}), 400)

	# check if there is no input error
	user_id = None
	adventure_id = None
	try:
		user_id = int(request.args['user_id'])
		adventure_id = int(request.args['adventure_id'])
	except:
		return make_response(jsonify({'error': 'Input error'}), 400)

	if (user_id >= 9223372036854775807) or (user_id < 0) or (adventure_id >= 9223372036854775807) or (adventure_id < 0):
		return make_response(jsonify({'error': 'Input error'}), 400)

	# check if adventure exists
	a = Adventure.query.filter_by(id=adventure_id).first()
	if (a is None) or (not a.is_active()):
		return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

	u = User.query.filter_by(id=user_id).first()
	if u is None:
		return make_response(jsonify({'error': 'User does not exists'}), 400)

	# check if creator_id match with user_id
	if a.creator_id != user_id:
		return make_response(jsonify({'error': 'User is not creator of adventure'}), 400)

	# delete adventure
	a.deleted = True
	a.deleted_on = datetime.now()
	db.session.commit()

	# make response
	return make_response(jsonify({'success': 'Adventure has been deleted'}), 200)
