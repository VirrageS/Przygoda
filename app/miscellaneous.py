# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import wraps
from flask.ext.login import current_user
from flask import redirect, url_for, flash, abort, make_response, jsonify, request
from app.users import constants as USER
from app import app

def confirmed_email_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if (current_user is None) or (current_user.confirmed is False):
			flash('Musisz potwierdzic swoj email zeby skorzystac z tej funkcji', 'danger')
			return redirect(url_for('simple_page.index'))

		return f(*args, **kwargs)
	return wrapper

def not_login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if current_user.is_authenticated():
			return redirect(url_for('simple_page.index'))

		return f(*args, **kwargs)
	return wrapper

def ssl_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if current_app.config.get("SSL"):
			if request.is_secure:
				return f(*args, **kwargs)
			else:
				return redirect(request.url.replace("http://", "https://"))

		return f(*args, **kwargs)
	return wrapper

# Usage @rule_required('admin', 'user')
def rule_required(*roles):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if str(current_user.role) not in roles:
			return abort(404)

		return f(*args, **kwargs)
	return wrapper

# decorator to filter no-admin users
def admin_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if (not current_user.is_authenticated()) or (current_user.role != USER.ADMIN):
			return abort(404)

		return f(*args, **kwargs)
	return wrapper

# function to add admin to database
def add_admin():
	# add admin
	from app.users.models import User
	from werkzeug import generate_password_hash
	from app.users import constants as USER
	from app import db

	u = User.query.filter_by(username="admin").first()
	if u is None:
		u = User("admin", generate_password_hash("supertajnehaslo"), "email@email.com", social_id=None)
		u.role = USER.ADMIN
		u.confirmed = True
		db.session.add(u)
		db.session.commit()

# decorator to compute time of the fuction
def execution_time(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		ts = datetime.now()
		result = f(*args, **kwargs)
		te = datetime.now()

		flash('%r (%r, %r) %s sec' % (f.__name__, args, kwargs, str(te-ts)), 'info')
		return result
	return wrapper

# compute days difference between two dates
def daterange(start_date, end_date):
	for n in range(int((end_date - start_date).days)):
		yield start_date + timedelta(n)

# decorator to filter no-api_key requests to api
def api_key_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if ('key' not in request.args) or (request.args["key"] != app.config["API_KEY"]):
			return make_response(jsonify({'error': 'No authenticated'}), 401)

		return f(*args, **kwargs)
	return wrapper
