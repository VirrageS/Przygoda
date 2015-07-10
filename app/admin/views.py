# -*- coding: utf-8 -*-

import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_user, logout_user, login_required
from flask.ext.sqlalchemy import get_debug_queries
from sqlalchemy.sql import func

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, AdventureParticipant
from app.mine.models import AdventureViews, AdventureSearches

from app.miscellaneous import admin_required

mod = Blueprint('admin', __name__, url_prefix='/admin')

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

# Admin panel
@mod.route('/')
@admin_required
def panel():
	return render_template('admin/panel.html')


@mod.route('/charts/')
@admin_required
def charts():
	def get_all_adventures():
		all_adventures = []
		adventures = Adventure.query.order_by(Adventure.created_on.asc()).all()

		active = 0
		count = 0
		participants = 0

		for adventure in adventures:
			count += 1
			if adventure.is_active():
				active += 1

			ap = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
			ap = list(filter(lambda ap: ap.is_active(), ap))
			participants += len(ap)

			all_adventures.append({
				'date': {
					'year': adventure.created_on.year,
					'month': adventure.created_on.month,
					'day': adventure.created_on.day,
					'hour': adventure.created_on.hour,
					'minute': adventure.created_on.minute,
					'second': adventure.created_on.second
				},
				'active': active,
				'count': count,
				'users_per_adventure': participants / count
			})

		return all_adventures

	def get_all_users():
		all_users = []
		users = User.query.order_by(User.registered_on.asc()).all()

		active = 0
		count = 0
		for user in users:
			if user.is_active_login():
				active += 1

			count += 1
			all_users.append({
				'date': {
					'year': user.registered_on.year,
					'month': user.registered_on.month,
					'day': user.registered_on.day,
					'hour': user.registered_on.hour,
					'minute': user.registered_on.minute,
					'second': user.registered_on.second
				},
				'active': active,
				'count': count
			})

		return all_users


	def get_users_per_adventure():
		all_users_per_adventure = []
		participants = AdventureParticipant.query.order_by(AdventureParticipant.joined_on).all()

		users = 0
		for participant in participants:
			users += 1

			registered_adventures = Adventure.query.filter(Adventure.created_on <= participant.joined_on).all()
			all_users_per_adventure.append({
				'date': {
					'year': participant.joined_on.year,
					'month': participant.joined_on.month,
					'day': participant.joined_on.day,
					'hour': participant.joined_on.hour,
					'minute': participant.joined_on.minute,
					'second': participant.joined_on.second
				},
				'users_per_adventure': users / len(registered_adventures)
			})

			# if participant.left_on is not None:
			# 	left_adventures = Adventure.query.filter(Adventure.created_on <= participant.left_on).all()
			# 	all_users_per_adventure.append({
			# 		'date': {
			# 			'year': participant.left_on.year,
			# 			'month': participant.left_on.month,
			# 			'day': participant.left_on.day,
			# 			'hour': participant.left_on.hour,
			# 			'minute': participant.left_on.minute,
			# 			'second': participant.left_on.second
			# 		},
			# 		'users_per_adventure': len(left_adventures)
			# 	})

		return all_users_per_adventure

	def get_adventures_views():
		all_adventures_views = []
		adventures = AdventureViews.query.add_column(func.count(AdventureViews.value)).group_by(AdventureViews.adventure_id).all()

		for adventure in adventures:
			all_adventures_views.append({
				'id': adventure[0].adventure_id,
				'views': adventure[1]
			})

		all_adventures_views = sorted(all_adventures_views, key=(lambda a: a['views']), reverse=True)
		return all_adventures_views

	def get_adventures_searches():
		all_adventures_searches = []
		adventures = AdventureSearches.query.add_column(func.count(AdventureSearches.value)).group_by(AdventureSearches.adventure_id).all()

		for adventure in adventures:
			all_adventures_searches.append({
				'id': adventure[0].adventure_id,
				'searches': adventure[1]
			})

		all_adventures_searches = sorted(all_adventures_searches, key=(lambda a: a['searches']), reverse=True)
		return all_adventures_searches

	return render_template(
		'admin/charts.html',
		all_adventures=get_all_adventures(),
		all_users=get_all_users(),
		all_users_per_adventure=get_users_per_adventure(),
		all_adventures_views=get_adventures_views(),
		all_adventures_searches=get_adventures_searches()
	)
