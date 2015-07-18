# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, flash, redirect, url_for
from sqlalchemy.sql import func

from app import app, db
from app.users.models import User
from app.adventures.models import Adventure, AdventureParticipant
from app.mine.models import AdventureViews, AdventureSearches, UserReports

from app.miscellaneous import admin_required

mod = Blueprint('admin', __name__, url_prefix='/admin')

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

		count = 0
		for adventure in adventures:
			count += 1
			active = Adventure.query.filter(
				Adventure.date > adventure.created_on,
				Adventure.created_on <= adventure.created_on
			).all()

			active = list(filter(
				lambda a: (
					(
						((a.deleted_on is not None) and (a.deleted_on > adventure.created_on)) or
						(a.deleted_on is None)
					)
					# ) and (
					# 	((a.disabled_on is not None) and (a.disabled_on > adventure.created_on)) or
					# 	(a.disabled_on is None)
					# )
				), active
			))

			all_adventures.append({
				'date': {
					'year': adventure.created_on.year,
					'month': adventure.created_on.month,
					'day': adventure.created_on.day,
					'hour': adventure.created_on.hour,
					'minute': adventure.created_on.minute,
					'second': adventure.created_on.second
				},
				'active': len(active),
				'count': count
			})

		return all_adventures

	def get_all_users():
		all_users = []
		users = User.query.order_by(User.registered_on.asc()).all()

		count = 0
		for user in users:
			active = User.query.filter(
				User.registered_on <= user.registered_on
			).all()

			User.last_login + timedelta(days=4) >= user.registered_on

			active = list(filter(
				lambda u: (
					((u.last_login is not None) and (u.last_login + timedelta(days=4) > user.registered_on)) or
					(u.last_login is None)
				), active
			))

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
				'active': len(active),
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
		adventures = db.session.query(
			AdventureViews.adventure_id.label('adventure_id'), func.sum(AdventureViews.value).label('views')
		).group_by(AdventureViews.adventure_id).all()

		for adventure in adventures:
			all_adventures_views.append({
				'id': adventure.adventure_id,
				'views': adventure.views
			})

		all_adventures_views = sorted(all_adventures_views, key=(lambda a: a['views']), reverse=True)
		return all_adventures_views

	def get_adventures_searches():
		all_adventures_searches = []
		adventures = db.session.query(
			AdventureSearches.adventure_id.label('adventure_id'), func.sum(AdventureSearches.value).label('searches')
		).group_by(AdventureSearches.adventure_id).all()

		for adventure in adventures:
			all_adventures_searches.append({
				'id': adventure.adventure_id,
				'searches': adventure.searches
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

# Reports
@mod.route('/reports/')
@admin_required
def reports():
	reports = UserReports.query.all()
	reports = list(filter(lambda r: r.display, reports))
	all_reports = sorted(reports, key=(lambda r: r.created_on))

	return render_template(
		'admin/reports.html',
		reports=all_reports
	)

# Hide report
@mod.route('/reports/hide/<int:report_id>')
@admin_required
def hide(report_id):
	report = UserReports.query.filter_by(id=report_id).first()
	if report is not None:
		report.display = False
		db.session.add(report)
		db.session.commit()

		flash('Raport został schowany', 'success')
		return redirect(url_for('admin.reports'))

	flash('Raport nie istnieje', 'danger')
	return redirect(url_for('admin.reports'))

# Users
@mod.route('/users/')
@admin_required
def users():
	all_users = User.query.all()

	return render_template(
		'admin/users.html',
		users=all_users
	)

# Adventures
@mod.route('/adventures/')
@admin_required
def adventures():
	all_adventures = Adventure.query.all()

	return render_template(
		'admin/adventures.html',
		adventures=all_adventures
	)
