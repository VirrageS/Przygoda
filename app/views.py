# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, flash, redirect, url_for

from flask.ext.login import current_user
from flask.ext.babel import gettext
from app.adventures.models import Adventure, Coordinate, AdventureParticipant
from app.adventures import constants as ADVENTURES
from app.miscellaneous import get_current_user_id
from app.recommender_system import get_recommended_adventures
from app.users.models import User
from app import cache, db

from app.mine.forms import ReportForm
from app.mine.models import UserReports

mod = Blueprint('simple_page', __name__, template_folder='templates')

#@cache.cached(timeout=5)
def show_all_adventures():
	all_adventures = {
		'most_recent': [],
		'start_soon': [],
		'top_adventures': []
	}

	recommended_adventures = get_recommended_adventures(get_current_user_id())

	for sort_type, adventures in recommended_adventures.items():
		for adventure in adventures:
			# get creator of the event and check if still exists
			user = User.query.filter_by(id=adventure.creator_id).first()
			if user is None:
				continue

			# get joined participants
			participants = adventure.get_participants()

			action = -1
			if current_user.is_authenticated():
				participant = AdventureParticipant.query.filter_by(adventure_id=adventure.id, user_id=current_user.id).first()
				if (participant is None) or (not participant.is_active()):
					action = 0
				else:
					action = 1

				if adventure.creator_id == current_user.id:
					action = -1

			coordinates = Coordinate.query.filter_by(adventure_id=adventure.id).all()
			markers = [(coordinate.latitude, coordinate.longitude) for coordinate in coordinates]

			all_adventures[sort_type].append({
				'id': adventure.id,
				'username': user.username,
				'date': adventure.date.strftime('%d.%m.%Y %H:%M'),
				'info': adventure.info,
				'joined': len(participants),
				'mode': ADVENTURES.MODES[int(adventure.mode)],
				'action': action,
				'markers': markers
			})

	return render_template(
		'all.html',
		most_recent=all_adventures['most_recent'],
		start_soon=all_adventures['start_soon'],
		top_adventures=all_adventures['top_adventures']
	)

# Index - main path
@mod.route("/")
def index():
	if not current_user.is_authenticated():
		return render_template('landing.html')

	return show_all_adventures()

# Show all adventures (if not logged in)
@mod.route("/all/")
def show_adventures():
	return show_all_adventures()

# About us
@mod.route("/about")
def about():
	return render_template('about.html')

# Contact
@mod.route("/contact/", methods=['GET', 'POST'])
def contact():

	form = ReportForm(request.form)

	if current_user.is_authenticated():
		form = ReportForm(request.form, obj=current_user)

	if form.validate_on_submit():
		user_id = None
		if current_user.is_authenticated():
			user_id = current_user.id

		report = UserReports(user_id=user_id, email=form.email.data, subject=form.subject.data, message=form.message.data)
		db.session.add(report)
		db.session.commit()

		flash(gettext(u'Message sent. Thank you for contact. We really appreciate it!'), 'success')
		return redirect(url_for('simple_page.index'))

	return render_template(
		'contact.html',
		form=form
	)

# How it works
@mod.route("/how-it-works")
def how_it_works():
	return render_template('how-it-works.html')

# Features in our app
@mod.route("/features")
def features():
	return render_template('features.html')

# Carrers - avaiable
@mod.route("/carrers")
def carrers():
	return render_template('carrers.html')

# Support
@mod.route("/support")
def support():
	return render_template('support.html')
