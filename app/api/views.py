# -*- coding: utf-8 -*-

from datetime import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, flash, redirect, url_for, make_response, jsonify
from flask.ext.login import current_user, login_user, logout_user, login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, AdventureParticipant

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
        'registered_on': u.registered_on
    }

    # curl -i http://127.0.0.1:5000/api/v1.0/login?username=tomek\&password=t

    return jsonify(response_user)

# User register
@mod.route('/user/register/', methods=['GET'])
def register():
    if 'username' not in request.args:
        return make_response(jsonify({'error': 'Username not provided'}), 400)

    if 'email' not in request.args:
        return make_response(jsonify({'error': 'Email not provided'}), 400)

    if 'password' not in request.args:
        return make_response(jsonify({'error': 'Password not provided'}), 400)

	# TODO: length of username/email/password must be checked!!

    u = User.query.filter_by(username=request.args['username'], email=request.args['email']).first()
    if u is not None:
        return make_response(jsonify({'error': 'User with username or email already exists'}), 400)

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
		'date': a.date,
		'mode': a.mode,
		'info': a.info,
		'joined': len(final_participants)
	}

	return jsonify(response_adventure)

@mod.route('/adventure/delete/', methods=['GET'])
def delete_adventure():
	if 'user_id' not in request.args:
		return make_response(jsonify({'error': 'User id not provided'}), 400)

	if 'adventure_id' not in request.args:
		return make_resposne(jsonify({'error': 'Adventure id not provied'}), 400)

	
	return jsonify('Hello')
