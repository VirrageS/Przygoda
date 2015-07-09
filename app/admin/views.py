# -*- coding: utf-8 -*-

import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_user, logout_user, login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure

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
	def get_active_adventures():
		adventures = Adventure.query.all()
		adventures = list(filter(lambda a: a.is_active(), adventures))
		return len(adventures)

	def get_inactive_adventures():
		adventures = Adventure.query.all()
		adventures = list(filter(lambda a: not a.is_active(), adventures))
		return len(adventures)

	def get_all_adventures():
		adventures = Adventure.query.all()
		return len(adventures)

	def get_all_users():
		users = User.query.all()
		return len(users)

	def get_users_per_adventure():
		adventures = Adventure.query.all()

		if len(adventures) == 0:
			return 0

		all_participants = 0
		for adventure in adventures:
			ap = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()
			all_participants += len(ap)

		return all_participants / len(adventures)


	return render_template('admin/charts.html')
