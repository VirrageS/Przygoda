# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from flask.ext.babel import gettext

from datetime import datetime, timedelta # for current date

from app import app, db
#from app.miscellaneous import confirmed_email_required
from app.adventures import constants as ADVENTURES
from app.adventures.miscellaneous import get_bounds, get_waypoints
from app.miscellaneous import get_current_user_id
from app.adventures.models import Adventure, AdventureParticipant, Coordinate
from app.adventures.forms import NewForm, EditForm, SearchForm
from app.users.models import User

from app.mine.models import AdventureSearches, AdventureViews

import googlemaps
gmaps = googlemaps.Client(key='AIzaSyA78hACcUKnn2S6cyy9gY5M8hVhiuxqhuE')

mod = Blueprint('adventures', __name__, url_prefix='/adventures')

@mod.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= app.config['DATABASE_QUERY_TIMEOUT']:
            app.logger.warning(
                "SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
                (query.statement, query.parameters, query.duration, query.context)
            )
    return response

# Show adventure with id
@mod.route('/<int:adventure_id>')
def show(adventure_id):
    """Show adventure"""

    # check if adventure_id is not max_int
    if adventure_id >= 9223372036854775807:
        return redirect(url_for('simple_page.index'))

    final_adventure = {}
    final_participants = []
    final_coordinates = []

    # get adventure and check if exists or is active
    adventure = Adventure.query.filter_by(id=adventure_id).first()
    if (adventure is None) or (not adventure.is_active()):
        flash(gettext(u'Adventure not found'), 'danger')
        return redirect(url_for('simple_page.index'))

    # get adventures creator and check if exists
    user = User.query.filter_by(id=adventure.creator_id).first()
    if user is None:
        flash(gettext(u'Creator not found'), 'danger')
        return redirect(url_for('simple_page.index'))

    # get joined participants
    participants = adventure.get_participants()

    for participant in participants:
        user = User.query.filter_by(id=participant.user_id).first()

        if user is not None:
            final_participants.append(user)


    # get avaiable action
    action = 'no-action'
    if current_user.is_authenticated():
        participant = AdventureParticipant.query.filter_by(adventure_id=adventure.id, user_id=current_user.id).first()
        if (participant is None) or (not participant.is_active()):
            action = 'join'
        else:
            action = 'leave'

        if adventure.creator_id == current_user.id:
            action = 'manage'

    final_adventure = {
        'id': adventure.id,
        'username': user.username,
        'date': adventure.date,
        'info': adventure.info,
        'joined': len(participants),
        'action': action
    }

    # update adventure views
    views = AdventureViews(user_id=get_current_user_id(), adventure_id=adventure.id)
    db.session.add(views)
    db.session.commit()

    # get coordinates of existing points
    coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
    final_coordinates = [(coordinate.latitude, coordinate.longitude) for coordinate in coordinates]

    return render_template(
        'adventures/show.html',
        adventure=final_adventure,
        participants=final_participants,
        markers=final_coordinates
    )

# Join to adventure with id
@mod.route('/join/<int:adventure_id>')
@login_required
def join(adventure_id):
    """Allow to join to existing adventure"""

    # check if adventure_id is not max_int
    if adventure_id >= 9223372036854775807:
        return redirect(url_for('simple_page.index'))

    # get adventure and check if exists
    adventure = Adventure.query.filter_by(id=adventure_id).first()
    if (adventure is None) or (not adventure.is_active()):
        flash(gettext(u'Adventure not found'), 'danger')
        return redirect(url_for('simple_page.index'))

    participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=current_user.id).first()

    # check if user joining adventure for the first time
    if participant is None:
        # add user to adventure participants to database
        participant = AdventureParticipant(adventure_id=adventure_id, user_id=current_user.id)
        db.session.add(participant)
        db.session.commit()
        flash(gettext(u'You successfully joined to Adventure'), 'success')
        return redirect(url_for('simple_page.index'))

    # check if user is rejoining
    if participant.is_active():
        flash(gettext(u'You have joined to this Adventure before'), 'warning')
        return redirect(url_for('simple_page.index'))

    # join user again
    participant.left_on = None
    participant.joined_on = datetime.now()
    db.session.add(participant)
    db.session.commit()

    flash(gettext(u'You successfully joined to Adventure'), 'success')
    return redirect(url_for('simple_page.index'))

@mod.route('/leave/<int:adventure_id>')
@login_required
def leave(adventure_id):
    """Allow to leave the adventure"""

    # check if adventure_id is not max_int
    if adventure_id >= 9223372036854775807:
        return redirect(url_for('simple_page.index'))

    # get adventure and check if exists
    adventure = Adventure.query.filter_by(id=adventure_id).first()
    if (adventure is None) or (not adventure.is_active()):
        flash(gettext(u'Adventure not found'), 'danger')
        return redirect(url_for('simple_page.index'))

    # check if user is the creator of the adventure
    if adventure.creator_id == current_user.id:
        flash(gettext(u'You cannot leave this Adventure'), 'warning')
        return redirect(url_for('simple_page.index'))

    participant = AdventureParticipant.query.filter_by(adventure_id=adventure_id, user_id=current_user.id).first()

    # check if user joined adventure
    if (participant is None) or (not participant.is_active()):
        flash(gettext(u'You have not joined this Adventure'), 'warning')
        return redirect(url_for('simple_page.index'))

    # delete user from adventure participants from database
    participant.left_on = datetime.now()
    db.session.commit()
    flash(gettext(u'You successfully left Adventure'), 'success')
    return redirect(url_for('simple_page.index'))

# Check all created and joined adventures
@mod.route('/my/')
@login_required
def my_adventures():
    """Show logged user's adventures"""

    final_created_adventures = []
    final_joined_adventures = []

    # get all adventures which created user
    created_adventures = Adventure.query.filter_by(creator_id=current_user.id).order_by(Adventure.date.asc()).all()
    created_adventures = [adventure for adventure in created_adventures if adventure.is_active()]

    for created_adventure in created_adventures:
        # get joined participants
        participants = created_adventure.get_participants()

        final_created_adventures.append({
            'id': created_adventure.id,
            'date': created_adventure.date,
            'info': created_adventure.info,
            'joined': len(participants)
        })

    # get all adventures to which user joined
    adventures_participant = AdventureParticipant.query.filter_by(user_id=current_user.id).all()
    joined_adventures_ids = [
        participant.adventure_id for participant in adventures_participant
            if participant.is_active()
    ]

    for joined_adventure_id in joined_adventures_ids:
        # get adventure
        adventure = Adventure.query.filter_by(id=joined_adventure_id).first()

        # check if user is not creator (we do not want duplicates) and if the adventure is active
        if (adventure is not None) and (adventure.is_active()) and (adventure.creator_id != current_user.id):
            final_joined_adventures.append(adventure)

    return render_template(
        'adventures/my.html',
        created_adventures=final_created_adventures,
        joined_adventures=final_joined_adventures
    )

# Edit adventure
@mod.route('/edit/<int:adventure_id>', methods=['GET', 'POST'])
@login_required
# @confirmed_email_required
def edit(adventure_id=0):
    """Allows to edit adventure"""

    # check if adventure_id is not max_int
    if adventure_id >= 9223372036854775807:
        return redirect(url_for('simple_page.index'))

    # get adventure
    adventure = Adventure.query.filter_by(id=adventure_id).first()

    # check if adventure exists
    if (adventure is None) or (not adventure.is_active()):
        flash(gettext(u'Adventure not found'), 'danger')
        return redirect(url_for('simple_page.index'))

    # check if user is creator of adventure
    if adventure.creator_id != current_user.id:
        flash(gettext(u'You cannot edit this Adventure'), 'danger')
        return redirect(url_for('simple_page.index'))

    # get joined participants
    final_participants = adventure.get_participants()

    # get form
    form = EditForm(request.form, obj=adventure)

    # verify the edit form
    if form.validate_on_submit():
        try:
            # get all waypoints
            waypoints = get_waypoints(request.form)

            if (waypoints is None) or (len(waypoints) < 2):
                flash(gettext(u'You must place at least two markers'), 'warning')
                return redirect(url_for('adventures.new'))

            # check if directions are good
            directions_result = gmaps.directions(
                origin=waypoints[0],
                destination=waypoints[-1],
                waypoints=[
                    waypoint for waypoint in waypoints
                        if ((waypoint is not waypoints[0]) and
                            (waypoint is not waypoints[-1]))
                ],
                mode="bicycling"
            )

            if (directions_result is None) or (not directions_result):
                flash(gettext(u'Not supported Adventure path'), 'warning')
                return redirect(url_for('simple_page.index'))

            # delete existing coordinates for the adventure_id
            db.session.query(Coordinate).filter_by(adventure_id=adventure_id).delete()
            db.session.commit()

            for i, waypoint in enumerate(waypoints):
                # add coordinates of adventure to database
                coordinate = Coordinate(
                    adventure_id=adventure.id,
                    path_point=i,
                    latitude=waypoint['lat'],
                    longitude=waypoint['lng']
                )
                db.session.add(coordinate)
                db.session.commit()

            # get edited adventure from the form
            form.populate_obj(adventure)

            # update adventure in database
            db.session.commit()
        except (googlemaps.exceptions.ApiError, googlemaps.exceptions.HTTPError, googlemaps.exceptions.TransportError):
            flash(gettext(u'Something went wrong'), 'danger')
            return redirect(url_for('simple_page.index'))

        # everything is okay
        flash(gettext(u'Adventure has been successfully created'), 'success')
        return redirect(url_for('simple_page.index'))

    # get coordinates of existing points
    coordinates = Coordinate.query.filter_by(adventure_id=adventure_id).all()
    final_coordinates = [(coordinate.latitude, coordinate.longitude) for coordinate in coordinates]

    return render_template(
        'adventures/edit.html',
        form=form,
        adventure_id=adventure_id,
        markers=final_coordinates,
        participants=final_participants,
        min_date=datetime.now().strftime("%m/%d/%Y %H:%M")
    )

# New adventure
@mod.route('/new/', methods=['GET', 'POST'])
@login_required
# @confirmed_email_required
def new():
    """Allows to create a new adventure"""

    # if new form has been submitted
    form = NewForm(request.form)

    # verify the new form
    if form.validate_on_submit():
        try:
            # get all waypoints
            waypoints = get_waypoints(request.form)

            if (waypoints is None) or (len(waypoints) < 2):
                flash(gettext(u'You must place at least two markers'), 'warning')
                return redirect(url_for('adventures.new'))

            # check if directions are good
            directions_result = gmaps.directions(
                origin=waypoints[0],
                destination=waypoints[-1],
                waypoints=[
                    waypoint for waypoint in waypoints
                        if ((waypoint is not waypoints[0]) and
                            (waypoint is not waypoints[-1]))
                ],
                mode="bicycling"
            )

            if (directions_result is None) or (not directions_result):
                flash(gettext(u'Not supported Adventure path'), 'warning')
                return redirect(url_for('adventures.new'))

            # add adventure to database
            adventure = Adventure(
                creator_id=current_user.id,
                date=form.date.data,
                mode=form.mode.data,
                info=form.info.data
            )
            db.session.add(adventure)
            db.session.commit()

            # add participant of adventure to database
            participant = AdventureParticipant(adventure_id=adventure.id, user_id=current_user.id)
            db.session.add(participant)
            db.session.commit()

            # add coordinates of adventure to database
            for i, waypoint in enumerate(waypoints):
                coordinate = Coordinate(
                    adventure_id=adventure.id,
                    path_point=i,
                    latitude=waypoint['lat'],
                    longitude=waypoint['lng']
                )
                db.session.add(coordinate)
                db.session.commit()

        except (googlemaps.exceptions.ApiError, googlemaps.exceptions.HTTPError, googlemaps.exceptions.TransportError):
            flash(gettext(u'Something went wrong'), 'danger')
            return redirect(url_for('adventures.new'))

        # everything is okay
        flash(gettext(u'Adventure has been successfully created'), 'success')
        return redirect(url_for('simple_page.index'))

    return render_template(
        'adventures/new.html',
        form=form,
        min_date=datetime.now().strftime("%m/%d/%Y %H:%M"),
        date=(datetime.now() + timedelta(hours=1)).strftime("%m/%d/%Y %H:%M")
    )

# Delete adventure
@mod.route('/delete/<int:adventure_id>')
@login_required
# @confirmed_email_required
def delete(adventure_id):
    """Allows to delete existing adventure"""

    # check if adventure_id is not max_int
    if adventure_id >= 9223372036854775807:
        return redirect(url_for('simple_page.index'))

    # get adventure
    adventure = Adventure.query.filter_by(id=adventure_id).first()

    # check if adventure exists
    if (adventure is None) or (not adventure.is_active()):
        flash(gettext(u'Adventure not found'), 'danger')
        return redirect(url_for('simple_page.index'))

    # check if user is creator of adventure
    if adventure.creator_id != current_user.id:
        flash(gettext(u'You cannot delete this Adventure'), 'danger')
        return redirect(url_for('simple_page.index'))

    # delete adventure
    adventure.deleted = True
    adventure.deleted_on = datetime.now()
    db.session.commit()

    flash(gettext(u'Adventure has been successfully deleted'), 'success')
    return redirect(url_for('simple_page.index'))

@mod.route('/search/', methods=['GET', 'POST'])
def search():
    """Allows to search adventures"""

    final_adventures = []
    final_coordinates = ()

    form = SearchForm(request.form)

    if form.validate_on_submit():
        # get bounds
        bounds = get_bounds(request.form)

        # check if bounds are good
        if bounds is None:
            flash(gettext(u'Something went wrong'), 'danger')
            return redirect(url_for('adventures.search'))

        # get adventures from area
        coordinates = Coordinate.query.filter(
            Coordinate.latitude >= bounds['bl_corner'][0],
            Coordinate.latitude <= bounds['tr_corner'][0],

            Coordinate.longitude >= bounds['bl_corner'][1],
            Coordinate.longitude <= bounds['tr_corner'][1]
        ).distinct(Coordinate.adventure_id).all()

        for coordinate in coordinates:
            # get adventure with coordinates id
            adventure = Adventure.query.filter_by(id=coordinate.adventure_id).first()

            # check if adventure is active
            if not adventure.is_active():
                continue

            check = False
            for mode in form.modes.data:
                if int(adventure.mode) == int(mode):
                    check = True

            if check:
                # get creator of the event
                user = User.query.filter_by(id=adventure.creator_id).first()

                # get joined participants
                participants = adventure.get_participants()

                # add to all adventures
                final_adventures.append({
                    'id': adventure.id,
                    'username': user.username,
                    'date': adventure.date,
                    'info': adventure.info,
                    'joined': len(participants),
                    'mode': ADVENTURES.MODES[int(adventure.mode)],
                })

                # update adventure search times
                searches = AdventureSearches(user_id=get_current_user_id(), adventure_id=adventure.id)
                db.session.add(searches)
                db.session.commit()

        # updated search coordinates
        final_coordinates = (bounds['bl_corner'], bounds['tr_corner'])

        # sort adventures by date
        final_adventures = sorted(final_adventures, key=(lambda a: a['date']))

        if final_adventures:
            flash(gettext(u'Below you can find some Adventures we have found for you'), 'success')
        else:
            flash(gettext(u'Unfortunately we have not found any Adventures for you. Try to change mode or area'), 'warning')

    return render_template(
        'adventures/search.html',
        form=form,
        adventures=final_adventures,
        coordinates=final_coordinates
    )
