# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from flask import Blueprint, render_template, flash, redirect, url_for, json
from sqlalchemy.sql import func

from app import app, db, cache
from app.users.models import User
from app.adventures.models import Adventure, AdventureParticipant
from app.mine.models import AdventureViews, AdventureSearches, UserReports

from app.miscellaneous import admin_required, execution_time, daterange

mod = Blueprint('admin', __name__, url_prefix='/admin')

# Charts
@mod.route('/charts/')
@admin_required
@cache.cached(timeout=120)
def charts():
    @execution_time
    def get_all_adventures(days):
        final_adventures = []

        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        for single_date in daterange(start_date, end_date):
            all_adventures = Adventure.query.filter(single_date >= Adventure.created_on).all()
            active_adventures = Adventure.query.filter(
                Adventure.date > single_date,
                Adventure.created_on < single_date
            ).all()

            active_adventures = [adventure for adventure in active_adventures if
                ((adventure.deleted_on is None) or (adventure.deleted_on > single_date)) and
                ((adventure.disabled_on is None) or (adventure.disabled_on > single_date))
            ]

            final_adventures.append({
                'date': single_date,
                'all': len(all_adventures),
                'active': len(active_adventures)
            })

        final_adventures = json.dumps(final_adventures)
        return final_adventures

    @execution_time
    def get_all_users(days):
        final_users = []

        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        for single_date in daterange(start_date, end_date):
            all_users = User.query.filter(single_date >= User.registered_on).all()

            active_users = User.query.filter(
                single_date >= User.registered_on,
                single_date <= User.last_login + timedelta(days=4)
            ).all()

            created_adventure = db.session.query(
                func.count(Adventure.creator_id).label('creator_id')
            ).filter(single_date >= Adventure.created_on).group_by(Adventure.creator_id).all()

            joined_to_adventure = db.session.query(
                func.count(AdventureParticipant.user_id).label('user_id')
            ).join(Adventure).filter(
                single_date >= AdventureParticipant.joined_on,
                AdventureParticipant.user_id != Adventure.creator_id
            ).group_by(AdventureParticipant.user_id).all()

            final_users.append({
                'date': single_date,
                'all': len(all_users),
                'active': len(active_users),
                'created_adventure': len(created_adventure),
                'joined_to_adventure': len(joined_to_adventure)
            })

        final_users = json.dumps(final_users)
        return final_users

    @execution_time
    def get_users_per_adventure(days):
        final_users_per_adventure = []

        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        for single_date in daterange(start_date, end_date):
            all_participants = AdventureParticipant.query.filter(single_date >= AdventureParticipant.joined_on).all()
            all_adventures = Adventure.query.filter(single_date >= Adventure.created_on).all()

            final_users_per_adventure.append({
                'date': single_date,
                'users_per_adventure': (0 if len(all_adventures) <= 0 else len(all_participants)/len(all_adventures))
            })

        final_users_per_adventure = json.dumps(final_users_per_adventure)
        return final_users_per_adventure

    @execution_time
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

        all_adventures_views = sorted(
            all_adventures_views,
            key=(lambda a: a['views']),
            reverse=True
        )

        return all_adventures_views

    @execution_time
    def get_adventures_searches():
        all_adventures_searches = []
        adventures = db.session.query(
            AdventureSearches.adventure_id.label('adventure_id'),
            func.sum(AdventureSearches.value).label('searches')
        ).group_by(AdventureSearches.adventure_id).all()

        for adventure in adventures:
            all_adventures_searches.append({
                'id': adventure.adventure_id,
                'searches': adventure.searches
            })

        all_adventures_searches = sorted(
            all_adventures_searches,
            key=(lambda a: a['searches']),
            reverse=True
        )

        return all_adventures_searches

    return render_template(
        'admin/charts.html',
        all_adventures=get_all_adventures(app.config['STATISTICS_DAYS_SPAN']),
        all_users=get_all_users(app.config['STATISTICS_DAYS_SPAN']),
        all_users_per_adventure=get_users_per_adventure(app.config['STATISTICS_DAYS_SPAN']),
        all_adventures_views=get_adventures_views(),
        all_adventures_searches=get_adventures_searches()
    )

# Reports
@mod.route('/reports/')
@admin_required
def show_all_reports():
    reports = UserReports.query.all()
    reports = [report for report in reports if report.display]
    sorted_reports = sorted(reports, key=(lambda r: r.created_on))

    return render_template(
        'admin/reports.html',
        reports=sorted_reports
    )

# Hide report
@mod.route('/reports/hide/<int:report_id>')
@admin_required
def hide_report(report_id):
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
def show_all_users():
    all_users = User.query.all()

    return render_template(
        'admin/users.html',
        users=all_users
    )

# Adventures
@mod.route('/adventures/')
@admin_required
def show_all_adventures():
    adventures = Adventure.query.all()

    all_adventures = []
    for adventure in adventures:
        status = 'no active'
        if adventure.is_active():
            status = 'active'

        adventure_participants = AdventureParticipant.query.filter_by(adventure_id=adventure.id).all()

        all_adventures.append({
            'id': adventure.id,
            'date': adventure.date,
            'info': adventure.info,
            'status': status,
            'joined': len(adventure_participants)
        })

    return render_template(
        'admin/adventures.html',
        adventures=all_adventures
    )
