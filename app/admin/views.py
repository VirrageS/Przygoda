# -*- coding: utf-8 -*-

import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_user, logout_user, login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, AdventureParticipant

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
			# if adventure.:
				# active += 1

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

	return render_template('admin/charts.html', all_adventures=get_all_adventures(), all_users=get_all_users())
