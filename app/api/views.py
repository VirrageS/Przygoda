# -*- coding: utf-8 -*-

from datetime import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, make_response, jsonify
from flask.ext.sqlalchemy import get_debug_queries

#from app.miscellaneous import api_key_required

from app import app, db
from app.users.models import User
from app.users.forms import RegisterForm
from app.adventures.models import Adventure, AdventureParticipant, Coordinate
from app.adventures import constants as ADVENTURES

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

    user = User.query.filter_by(email=request.args['email']).first()
    if user is None:
        return make_response(jsonify({'error': 'User not found'}), 400)

    if not check_password_hash(user.password, request.args['password']):
        return make_response(jsonify({'error': 'Password not correct'}), 400)

    response_user = {
        'id': user.id,
        'social_id': user.social_id,
        'username': user.username,
        'email': user.email,
        'registered_on': int(user.registered_on.strftime('%s'))
    }

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
        return make_response(
            jsonify({'error': 'Confirm password not provided'}), 400
        )

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

    new_user = User(
        username=request.args['username'],
        email=request.args['email'],
        password=generate_password_hash(request.args['password'])
    )

    db.session.add(new_user)
    db.session.commit()
    return make_response(jsonify({'success': 'User has been created'}), 201)

# Get user adventures
@mod.route('/user/get/adventures', methods=['GET'])
def get_user_adventures():
    if ('user_id' not in request.args) or (request.args['user_id'] == ''):
        return make_response(jsonify({'error': 'User id not provided'}), 400)

    # check if there is no input error
    user_id = None
    try:
        user_id = int(request.args['user_id'])
    except:
        return make_response(jsonify({'error': "Input error"}), 400)

    if (user_id >= 9223372036854775807) or (user_id < 0):
        return make_response(jsonify({'error': "Input error"}), 400)

    # check if adventure exists
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)

    final_adventures = {}
    final_created_adventures = {}
    final_joined_adventures = {}

    # get adventures created by user_id
    created_adventures = Adventure.query.filter_by(creator_id=user_id).order_by(Adventure.date.asc()).all()

    # filter active
    created_adventures = [
        adventure for adventure in created_adventures
            if adventure.is_active()
    ]

    for created_adventure in created_adventures:
        # get joined participants
        final_participants = {}
        participants = created_adventure.get_participants()

        for participant in participants:
            user_participant = User.query.filter_by(id=participant.user_id).first()

            if user is not None:
                final_participants[user_participant.id] = {
                    'id': user_participant.id,
                    'username': user_participant.username,
                    'joined_on': int(participant.joined_on.strftime('%s'))
                }

        # get static image url
        static_image_url = '' + \
            'https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg' + \
            '&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off' + \
            '&style=feature:road|element:labels.text.fill|color:0x959595' + \
            '&style=feature:poi|element:all|visibility:off' + \
            '&style=feature:administrative|element:all|visiblity:off' + \
            '&path=color:0x0000ff|weight:5'

        # get all coordinates
        final_coordinates = {}
        coordinates = Coordinate.query.filter_by(adventure_id=created_adventure.id).all()
        for coordinate in coordinates:
            final_coordinates[coordinate.path_point] = {
                'latitude': coordinate.latitude,
                'longitude': coordinate.longitude
            }

            static_image_url += '|' + str(coordinate.latitude) + ',' + str(coordinate.longitude)

        # add everything
        final_created_adventures[created_adventure.id] = {
            'id': created_adventure.id,
            'creator_id': user.id,
            'creator_username': user.username,
            'date': int(created_adventure.date.strftime('%s')),
            'mode': created_adventure.mode,
            'mode_name': ADVENTURES.MODES[created_adventure.mode],
            'info': created_adventure.info,
            'joined': len(final_participants),
            'participants': final_participants,
            'coordinates': final_coordinates,
            'static_image_url': static_image_url
        }

    # get all adventures to which user joined
    adventures_participant = AdventureParticipant.query.filter_by(user_id=user_id).all()
    joined_adventures_ids = [
        participant.adventure_id for participant in adventures_participant
            if participant.is_active()
    ]

    for joined_adventure_id in joined_adventures_ids:
        # get adventure
        adventure = Adventure.query.filter_by(id=joined_adventure_id).first()

        # check if user is not creator (we do not want duplicates)
        if (adventure is None) or (not adventure.is_active()) or (adventure.creator_id == user_id):
            continue

        # get creator and check if exists
        creator = User.query.filter_by(id=adventure.creator_id).first()
        if creator is None:
            continue

        # get joined participants
        final_participants = {}
        participants = adventure.get_participants()

        for participant in participants:
            user_participant = User.query.filter_by(id=participant.user_id).first()

            if user is not None:
                final_participants[user_participant.id] = {
                    'id': user_participant.id,
                    'username': user_participant.username,
                    'joined_on': int(participant.joined_on.strftime('%s'))
                }

        # get static image url
        static_image_url = 'https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg' + \
            '&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off' + \
            '&style=feature:road|element:labels.text.fill|color:0x959595' + \
            '&style=feature:poi|element:all|visibility:off' + \
            '&style=feature:administrative|element:all|visiblity:off' + \
            '&path=color:0x0000ff|weight:5'

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
        final_joined_adventures[adventure.id] = {
            'id': adventure.id,
            'creator_id': creator.id,
            'creator_username': creator.username,
            'date': int(adventure.date.strftime('%s')),
            'mode': adventure.mode,
            'mode_name': ADVENTURES.MODES[adventure.mode],
            'info': adventure.info,
            'joined': len(final_participants),
            'participants': final_participants,
            'coordinates': final_coordinates,
            'static_image_url': static_image_url
        }

    final_adventures = {
        'created': final_created_adventures,
        'joined': final_joined_adventures
    }

    return make_response(jsonify(final_adventures), 200)


# Adventure get
@mod.route('/adventure/get/<int:adventure_id>', methods=['GET'])
# @api_key_required
def get_adventure(adventure_id):
    if adventure_id >= 9223372036854775807:
        return make_response(jsonify({'error': 'Adventure id is too large'}), 400)

    adventure = Adventure.query.filter_by(id=adventure_id).first()
    if (adventure is None) or (not adventure.is_active()):
        return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

    # check if creator of the adventure exists
    creator = User.query.filter_by(id=adventure.creator_id).first()
    if creator is None:
        return make_response(jsonify({'error': 'Creator of adventure does not exists'}), 400)

    # get joined participants
    final_participants = {}
    participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
    participants = [participant for participant in participants if participant.is_active()]

    for participant in participants:
        user = User.query.filter_by(id=participant.user_id).first()

        if user is not None:
            final_participants[user.id] = {
                'id': user.id,
                'username': user.username,
                'joined_on': int(participant.joined_on.strftime('%s'))
            }

    # get static image url
    static_image_url = 'https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg' + \
        '&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off' + \
        '&style=feature:road|element:labels.text.fill|color:0x959595' + \
        '&style=feature:poi|element:all|visibility:off' + \
        '&style=feature:administrative|element:all|visiblity:off' + \
        '&path=color:0x0000ff|weight:5'

    # get all coordinates
    final_coordinates = {}
    coordinates = Coordinate.query.filter_by(adventure_id=adventure.id).all()
    for coordinate in coordinates:
        final_coordinates[coordinate.path_point] = {
            'latitude': coordinate.latitude,
            'longitude': coordinate.longitude
        }

        # add coordinates to static map url
        static_image_url += '|' + str(coordinate.latitude) + ',' + str(coordinate.longitude)

    final_adventure = {
        'id': adventure.id,
        'creator_id': creator.id,
        'creator_username': creator.username,
        'date': int(adventure.date.strftime('%s')),
        'mode': adventure.mode,
        'mode_name': ADVENTURES.MODES[adventure.mode],
        'info': adventure.info,
        'joined': len(final_participants),
        'participants': final_participants,
        'coordinates': final_coordinates,
        'static_image_url': static_image_url
    }

    return make_response(jsonify(final_adventure), 200)

@mod.route('/adventure/get/all/')
def get_all_adventures():
    final_adventures = {}

    # get all adventures
    adventures = Adventure.query.order_by(Adventure.date.asc()).all()
    adventures = [adventure for adventure in adventures if adventure.is_active()] # filter active

    for adventure in adventures:
        # get creator and check if exists
        creator = User.query.filter_by(id=adventure.creator_id).first()
        if creator is None:
            continue

        # get joined participants
        final_participants = {}
        participants = adventure.get_participants()

        for participant in participants:
            user = User.query.filter_by(id=participant.user_id).first()

            if user is not None:
                final_participants[user.id] = {
                    'id': user.id,
                    'username': user.username,
                    'joined_on': int(participant.joined_on.strftime('%s'))
                }

        # get static image url
        static_image_url = 'https://maps.googleapis.com/maps/api/staticmap?size=160x160&scale=2&format=jpg' + \
            '&style=feature:road|element:all|visibility:on&style=feature:road|element:labels.icon|visibility:off' + \
            '&style=feature:road|element:labels.text.fill|color:0x959595' + \
            '&style=feature:poi|element:all|visibility:off' + \
            '&style=feature:administrative|element:all|visiblity:off' + \
            '&path=color:0x0000ff|weight:5'

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
            'creator_username': creator.username,
            'date': int(adventure.date.strftime('%s')),
            'mode': adventure.mode,
            'mode_name': ADVENTURES.MODES[adventure.mode],
            'info': adventure.info,
            'joined': len(final_participants),
            'participants': final_participants,
            'coordinates': final_coordinates,
            'static_image_url': static_image_url
        }

    return make_response(jsonify(final_adventures), 200)


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

    if (user_id >= 9223372036854775807) or (user_id < 0):
        return make_response(jsonify({'error': 'Input error'}), 400)

    if (adventure_id >= 9223372036854775807) or (adventure_id < 0):
        return make_response(jsonify({'error': 'Input error'}), 400)

    # check if adventure exists
    adventure = Adventure.query.filter_by(id=adventure_id).first()
    if (adventure is None) or (not adventure.is_active()):
        return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)

    # check if creator_id match with user_id
    if adventure.creator_id == user_id:
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

    if (user_id >= 9223372036854775807) or (user_id < 0):
        return make_response(jsonify({'error': 'Input error'}), 400)

    if (adventure_id >= 9223372036854775807) or (adventure_id < 0):
        return make_response(jsonify({'error': 'Input error'}), 400)

    # check if adventure exists
    adventure = Adventure.query.filter_by(id=adventure_id).first()
    if (adventure is None) or (not adventure.is_active()):
        return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
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

    if (user_id >= 9223372036854775807) or (user_id < 0):
        return make_response(jsonify({'error': 'Input error'}), 400)

    if (adventure_id >= 9223372036854775807) or (adventure_id < 0):
        return make_response(jsonify({'error': 'Input error'}), 400)

    # check if adventure exists
    adventure = Adventure.query.filter_by(id=adventure_id).first()
    if (adventure is None) or (not adventure.is_active()):
        return make_response(jsonify({'error': 'Adventure does not exists'}), 400)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return make_response(jsonify({'error': 'User does not exists'}), 400)

    # check if creator_id match with user_id
    if adventure.creator_id != user_id:
        return make_response(jsonify({'error': 'User is not creator of adventure'}), 400)

    # delete adventure
    adventure.deleted = True
    adventure.deleted_on = datetime.now()
    db.session.commit()

    # make response
    return make_response(jsonify({'success': 'Adventure has been deleted'}), 200)
