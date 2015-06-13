from datetime import datetime
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

from app import db
from app.adventures.models import Adventure

mod = Blueprint('adventures', __name__, url_prefix='/adventures')

# New trip
@mod.route('/new/', methods=['GET', 'POST'])
@login_required
def new():
	if request.method == 'POST':
		if not request.form['info']:
			flash('Info is required', 'error')
		else:
			adventure = Adventure(g.user.username, datetime.utcnow(), request.form['info'], 1)
			db.session.add(adventure)
			db.session.commit()
			flash(u'Adventure item was successfully created')
			return redirect(url_for('index'))

	return render_template('adventures/new.html')

@mod.route('/adventures/')
@login_required
def adventures():
	return render_template('adventure/new.html')
