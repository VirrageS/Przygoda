from datetime import datetime
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

from app import db
from app.adventures.models import Adventure, AdventureParticipant
from app.adventures.forms import NewForm

mod = Blueprint('adventures', __name__, url_prefix='/adventures')

# New trip
@mod.route('/new/', methods=['GET', 'POST'])
@login_required
def new():
	# if new form has been submitted
	form = NewForm(request.form)

	if request.method == 'GET':
		return render_template('adventures/new.html', form=form)

	# verify the new form
	if form.validate_on_submit():
		# add adventure to database
		adventure = Adventure(user_id=g.user.id, date=form.date.data, info=form.info.data, joined=1)
		db.session.add(adventure)
		db.session.commit()

		# add participant of adventure to database
		adventureParticipant = AdventureParticipant(adventure_id=adventure.id, user_id=g.user.id)
		db.session.add(adventureParticipant)
		db.session.commit()

		# everything is okay
		flash('Adventure item was successfully created')
		return redirect(url_for('simple_page.index'))

	return render_template('adventures/new.html', form=form)

@mod.route('/<int:adventure_id>')
def adventure_show(adventure_id):
	flash(adventure_id)
	return render_template('adventures/show.html', adventure_id=adventure_id)

@mod.route('/join/<int:adventure_id>')
@login_required
def join(adventure_id):
	return render_template('adventures/my.html')

@mod.route('/my/')
@login_required
def my_adventures():
	return render_template('adventures/my.html')
