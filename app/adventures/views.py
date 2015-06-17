from datetime import datetime
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

from app import db
from app.adventures.models import Adventure
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
		adventure = Adventure(user_id=g.user.id, date=form.date.data, info=form.info.data, joined=1)

		# add adventure to database
		db.session.add(adventure)
		db.session.commit()
		flash('Adventure item was successfully created')
		return redirect(url_for('simple_page.index'))

	return render_template('adventures/new.html', form=form)

@mod.route('/join/')
def join():
	return render_template('adventure/new.html')

@mod.route('/my/')
@login_required
def my_adventures():
	return render_template('adventure/my.html')
